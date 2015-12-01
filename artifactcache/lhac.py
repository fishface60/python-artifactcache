#!/usr/bin/python

from contextlib import contextmanager
from os.path import join
from shutil import rmtree
from subprocess import check_call
from tempfile import mkdtemp

try:
	from contextlib import ExitStack
except ImportError:
	from contextlib2 import ExitStack
from flock import lockfile

@contextmanager
def _tempdir(*args, **kwargs):
	td = mkdtemp(*args, **kwargs)
	try:
		yield td
	finally:
		rmtree(td)

class LHAC(object):

	@contextmanager
	def _locked_tempdir(self, dir=None, **kwargs):
		with lockfile(self._basedir) as cachelock:
			cachelock.lock(shared=False, timeout=0)
			with _tempdir(dir=self._basedir, **kwargs) as tmpdir, \
		     	     lockfile(tmpdir) as tmplock:
				tmplock.lock(shared=False, timeout=0)
				cachelock.unlock()
				yield (tmpdir, tmplock)

	def _hardlink_artifact(self, artifact, composedir)
		artifactdir = join(self._basedir, artifact)
		with lockfile(artifactdir) as artifactlock:
			artifactlock.lock(shared=True)
			check_call(['cp', '-al', join(artifactdir, 'tree'),
			            composedir])

	@contextmanager
	def compose(self, source_artifacts=()):
		with self._locked_tempdir(prefix='compose.') \
		as (composedir, composelock), \
		     lockfile(self._basedir) as cachelock:
			cachelock.lock(shared=True, timeout=0)
			for artifact in source_artifacts:
				self._hardlink_artifact(artifact,
				                        composedir)
			composelock.lock(shared=True, timeout=0)
			cachelock.unlock()
			yield (composedir, composelock)

	@contextmanager
	def save(self, artifacts_to_files):
		with ExitStack() as es:
			savedir, savelock = es.enter_context(
			    self._locked_tempdir(prefix='save.'))
			artifact_state = {}
			# make and lock all artifacts,
			# so concurrent creation can be detected

			# at which point the process that failed to lock 
			# releases all artifact locks,
			# and may instead opt to compose an artifact to wait
			# for completion.

			for artifact in sorted(artifacts_to_files):
				artifact_state[artifact] = es.enter_context(
				    self._locked_tempdir(prefix='artifact.'))
			
			# Yield to allow caller to put files in
			yield (savedir, savelock)
			
			# Populate artifact tempdirs
			for artifact in artifact_state:
				tempdir, lock = artifact_state[artifact]
				tree = join(tempdir, 'tree')
				files = artifacts_to_files[artifact]
				cmd = ['cpio', '-pl', tree]
				p = Popen(cmd, cwd=savedir, stderr=STDOUT)
				out, _ = p.communicate('\0'.join(files))
				ret = p.wait()
				if ret != 0:
					raise CalledProcessError(ret, cmd, out)
			
			# Move all artifacts into place
			partialartifactcleanup = es.enter_context(ExitStack())
			for artifact in artifact_state:
				final = join(self._basedir, artifact)
				tempdir, _ = artifact_state[artifact]
				rename(tempdir, final)
				# Remove artifact if any renames fail
				partialartifactcleanup.callback(rmtree, final)
			
			# Make artifacts usable now
			for artifact in sorted(artifact_state):
				tempdir, lock = artifact_state[artifact]
				lock.lock(shared=True, timeout=0)
			
			# Don't cleanup artifacts in-use
			partialartifactcleanup.pop_all()
