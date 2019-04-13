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

with pkgs;

stdenv.mkDerivation {
  name = "j5-dev-env";
  buildInputs = [
    gnumake
    graphviz  # for docs
    python3
    python3Packages.poetry
  ];
  LD_LIBRARY_PATH = [ "${libusb1}/lib" ];
}
