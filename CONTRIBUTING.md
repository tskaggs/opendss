# Contributing

Thanks for your interest in improving OpenDSS.

## Development setup

See the [README](README.md) for:

- Backend: Python venv, `pip install -r backend/requirements.txt`, `uvicorn app.main:app --reload` from `backend/`
- Frontend: `pnpm install` and `pnpm dev` in `frontend/`

## Pull requests

- Keep changes focused on one topic (feature, fix, or docs).
- Match existing code style (TypeScript / Vue in `frontend/`, Python in `backend/`).
- Run `pnpm run build` in `frontend/` before submitting UI changes when practical.
- For Python, ensure the app still imports (`python -c "from app.main import app"` from `backend/`).

## Security

If you believe you have found a security vulnerability, please follow [SECURITY.md](SECURITY.md) instead of opening a public issue.

## License

By contributing, you agree that your contributions are licensed under the same terms as the project ([LICENSE](LICENSE)).
