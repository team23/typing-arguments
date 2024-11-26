default:
    just --list

[unix]
_install-pre-commit:
    #!/usr/bin/env bash
    if ( which pre-commit > /dev/null 2>&1 )
    then
        pre-commit install --install-hooks
    else
        echo "-----------------------------------------------------------------"
        echo "pre-commit is not installed - cannot enable pre-commit hooks!"
        echo "Recommendation: Install pre-commit ('brew install pre-commit')."
        echo "-----------------------------------------------------------------"
    fi

[windows]
_install-pre-commit:
    #!powershell.exe
    Write-Host "Please ensure pre-commit hooks are installed using 'pre-commit install --install-hooks'"

install: (uv "sync") && _install-pre-commit

update: (uv "sync")

uv *args:
    uv {{args}}

test *args: (uv "run" "pytest" "--cov=typing_arguments" "--cov-report" "term-missing:skip-covered" args)

test-all: (uv "run" "tox")

ruff *args: (uv "run" "ruff" "check" "typing_arguments" "tests" args)

pyright *args: (uv "run" "pyright" "typing_arguments" args)

lint: ruff pyright

publish: (uv "publish" "--build")

release version: (uv "run" "pkg-version.py" version)
    git add pyproject.toml
    git commit -m "release: 🔖 v$(uv run --quiet pkg-version.py)" --no-verify
    git tag "v$(uv run --quiet pkg-version.py)"
    git push
    git push --tags
