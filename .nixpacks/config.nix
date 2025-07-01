{ pkgs }:
{
  packages = [
    pkgs.python312
    pkgs.python312Packages.setuptools
    pkgs.python312Packages.wheel
    pkgs.python312Packages.pip
  ];
}
