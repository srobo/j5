{
  pkgsSrc ? <nixpkgs>,
  pkgs ? import pkgsSrc {}
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
}
