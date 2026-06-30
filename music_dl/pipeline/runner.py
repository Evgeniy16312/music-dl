from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from yandex_music import Client

from music_dl.console import console, print_lock
from music_dl.core.cancel import is_cancel_requested, raise_if_cancelled
from music_dl.core.filenames import sanitize_filename
from music_dl.core.models import DownloadOptions, DownloadStats, TrackCollection, TrackJob
from music_dl.pipeline.failed_log import failed_log_path, load_failed_log, save_failed_log
from music_dl.pipeline.jobs import build_jobs
from music_dl.providers.yandex.metadata import create_client
from music_dl.providers.yandex.track_download import run_yandex_worker

WorkerFn = Callable[[str, TrackJob, DownloadOptions], tuple[str, dict | None]]


def _apply_result(
    stats: DownloadStats,
    result: str,
    failed_entry: dict | None,
    job: TrackJob,
) -> None:
    with print_lock:
        if result == "downloaded":
            stats.downloaded += 1
            console.print(f"[green]  ok[/green]    {job.dest.name}")
        elif result == "skipped":
            stats.skipped += 1
            console.print(f"[dim]  skip[/dim]  {job.dest.name}")
        else:
            stats.failed += 1
            if failed_entry:
                stats.failed_entries.append(failed_entry)
            error = failed_entry["error"] if failed_entry else "unknown"
            console.print(f"[red]  fail[/red]  {job.dest.name}: {error}")


def run_download_jobs(
    token: str,
    jobs: list[TrackJob],
    opts: DownloadOptions,
    worker: WorkerFn = run_yandex_worker,
) -> DownloadStats:
    stats = DownloadStats()
    if not jobs:
        return stats

    if opts.dry_run:
        for job in jobs:
            action = "skip" if opts.skip_existing and job.dest.exists() else "download"
            console.print(f"[{job.number}/{job.total}] {action:8} {job.dest.name}")
        return stats

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=False,
    )

    cancelled = False

    with progress:
        task_id = progress.add_task("Скачивание", total=len(jobs))

        if opts.workers <= 1:
            for job in jobs:
                try:
                    raise_if_cancelled()
                except KeyboardInterrupt:
                    cancelled = True
                    break
                progress.update(
                    task_id,
                    description=f"[{job.number}/{job.total}] {job.dest.name[:50]}",
                )
                result, failed_entry = worker(token, job, opts)
                _apply_result(stats, result, failed_entry, job)
                progress.advance(task_id)
        else:
            pool = ThreadPoolExecutor(max_workers=opts.workers)
            try:
                futures = {pool.submit(worker, token, job, opts): job for job in jobs}
                pending = set(futures.keys())
                while pending:
                    if is_cancel_requested():
                        cancelled = True
                        for future in pending:
                            future.cancel()
                        break
                    done, pending = wait(
                        pending, timeout=0.5, return_when=FIRST_COMPLETED
                    )
                    for future in done:
                        job = futures[future]
                        progress.update(
                            task_id,
                            description=f"[{job.number}/{job.total}] {job.dest.name[:50]}",
                        )
                        result, failed_entry = future.result()
                        _apply_result(stats, result, failed_entry, job)
                        progress.advance(task_id)
            except KeyboardInterrupt:
                cancelled = True
            finally:
                pool.shutdown(wait=False, cancel_futures=True)

    if cancelled or is_cancel_requested():
        console.print("[yellow]Скачивание прервано (Ctrl+C)[/yellow]")
    return stats


def download_collection(
    client: Client,
    token: str,
    collection: TrackCollection,
    opts: DownloadOptions,
) -> DownloadStats:
    out_dir = opts.output
    if not opts.flat:
        out_dir = out_dir / sanitize_filename(collection.label)

    jobs = build_jobs(collection, out_dir, opts)
    console.print(f"[bold]{collection.label}[/bold]: {len(jobs)} трек(ов) → {out_dir}")
    stats = run_download_jobs(token, jobs, opts)
    save_failed_log(failed_log_path(out_dir), stats.failed_entries)
    if stats.failed_entries:
        console.print(f"[yellow]Ошибки сохранены: {failed_log_path(out_dir)}[/yellow]")
    return stats


def retry_failed(token: str, log_path: Path, opts: DownloadOptions) -> DownloadStats:
    entries = load_failed_log(log_path)
    jobs: list[TrackJob] = []
    for index, entry in enumerate(entries, start=1):
        track_id = int(entry["track_id"])
        dest = Path(entry["dest"])
        tracks = create_client(token).tracks(track_id)
        if not tracks:
            console.print(f"[red]Трек {track_id} не найден, пропуск[/red]")
            continue
        jobs.append(
            TrackJob(number=index, total=len(entries), item=tracks[0], dest=dest)
        )

    console.print(f"Повтор: {len(jobs)} трек(ов) из {log_path}")
    stats = run_download_jobs(token, jobs, opts)
    save_failed_log(log_path, stats.failed_entries)
    return stats
