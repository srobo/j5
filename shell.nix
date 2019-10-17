# XXX poetry is broken on nixos-19.09 so we have to pin to nixos-19.03

{
  pkgsSrc ? (fetchTarball https://nixos.org/channels/nixos-19.03/nixexprs.tar.xz),
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
