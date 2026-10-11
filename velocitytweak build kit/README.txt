VELOCITY PC OPTIMIZER — WINDOWS DESKTOP STARTER

Included files:
- velocity_optimizer.py: Windows desktop app source
- Run Velocity.bat: run from source (requires Python)
- Build EXE on this PC.bat: builds a standalone EXE locally (requires Python for building)
- .github/workflows/build-windows-exe.yml: builds the standalone EXE on a Windows runner in GitHub Actions

GET A STANDALONE EXE WITHOUT INSTALLING PYTHON ON YOUR PC
This workspace runs on Linux, so it cannot directly compile a proper Windows EXE here. The included GitHub Actions workflow builds it on a Windows machine in the cloud. You only need to do this setup once:

1. Sign in to GitHub and create a new repository (a private repository is fine).
2. Upload the contents of this folder to the repository, including the hidden .github folder and its workflow file. Easiest: extract the ZIP, then use GitHub's web upload; if the web interface doesn't show hidden files, use GitHub Desktop or the Git command line so .github/workflows/build-windows-exe.yml is included.
3. Open the repository's Actions tab.
4. Choose “Build Velocity Windows EXE” in the workflow list.
5. Click “Run workflow” if it has not started automatically after upload.
6. Open the completed workflow run. At the bottom, download the artifact named “VelocityPCOptimizer-Windows-x64”.
7. Extract the downloaded artifact ZIP. Double-click VelocityPCOptimizer.exe. The built app does not require Python installed on the target PC.

LOCAL BUILD OPTION
On a Windows PC with Python 3.10+ installed, double-click “Build EXE on this PC.bat”. The output is dist\VelocityPCOptimizer.exe. Python is only needed for the build process; the resulting EXE bundles the runtime.

APP SAFETY
- Only offers a hard-coded allowlist of optional desktop applications.
- Does not kill arbitrary processes or stop Windows services.
- Does not target Windows core processes, Defender/security tools, drivers, or anti-cheat.
- Closing apps can lose unsaved work or interrupt calls, streams, uploads, game launchers, and peripheral profiles. Read the confirmation prompt carefully.
- Windows may refuse to close an app or it may restart itself.
- No administrator privileges are requested by design.

LOG
Action log: %LOCALAPPDATA%\VelocityOptimizer\actions.log

LIMITATIONS
This starter app does not implement registry tweaks or guarantee FPS gains. Benchmark your games before and after changes. Exact hardware details vary by Windows APIs.
