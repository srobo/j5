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

# Note that as of 2019-01-21, pipenv is currently broken in the NixOS 18.09 release.
# https://github.com/NixOS/nixpkgs/issues/51970
# To work around, invoke with:
# nix-shell -E 'import ./shell.nix { pkgsSrc = fetchTarball https://nixos.org/channels/nixpkgs-unstable/nixexprs.tar.xz; }'

with pkgs;

stdenv.mkDerivation {
  name = "j5-dev-env";
  buildInputs = [
    pipenv
    python3
  ];
  LD_LIBRARY_PATH = [ "${libusb1}/lib" ];
}
