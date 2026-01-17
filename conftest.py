#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

from pathlib import Path

import pytest


def pytest_collect_file(parent, file_path):
	"""Collect files named like '*.test.py' safely.

	A filename containing '.' (e.g. 'job_title.test.py') makes pytest try to
	import it as module 'job_title.test', which fails because 'job_title' is not
	a package. We override the module name to a safe identifier.
	"""

	p = Path(str(file_path))
	if not p.name.endswith(".test.py"):
		return None

	safe_name = p.name.replace(".", "_")
	return pytest.Module.from_parent(parent, path=file_path, name=safe_name)

