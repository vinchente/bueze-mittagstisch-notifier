from invoke import task, Collection, Context


@task
def test(ctx: Context) -> None:
    ctx.run("ruff check")
    ctx.run("ruff format --check")
    ctx.run("mypy")
    ctx.run("pytest -x --ff --cov=bueze_mittagstisch_notifier --cov-report=term --cov-report=xml")

@task
def fix(ctx: Context) -> None:
    ctx.run("ruff check --fix")
    ctx.run("ruff format")


ns = Collection(test, fix)
ns.configure({"run": {"echo": True, "pty": True}})
