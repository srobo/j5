# A nixpkgs overlay to set python3Packages to python37Packages (the default is python36Packages).
let
  python37ByDefault = self: super: {
    python3Packages = self.python37Packages;
  };
in

{
  pkgsSrc ? <nixpkgs>,
  pkgs ? import pkgsSrc { overlays = [python37ByDefault]; },
}:

# Note that as of 2019-03-11, poetry is not currently available in any nixpkgs release.
# To work around, invoke with:
# nix-shell --arg pkgsSrc 'fetchTarball https://github.com/NixOS/nixpkgs/archive/master.tar.gz'
# It should appear in NixOS/nixpkgs 19.03.

with pkgs;

stdenv.mkDerivation {
  name = "j5-dev-env";
  buildInputs = [
    gnumake
    python3
    python3Packages.poetry
  ];
  LD_LIBRARY_PATH = [ "${libusb1}/lib" ];
}
