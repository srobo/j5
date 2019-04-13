{
  pkgsSrc ? <nixpkgs>,
  pkgs ? import pkgsSrc {},
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
