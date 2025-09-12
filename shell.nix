{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {

  buildInputs = [
    (pkgs.python312.withPackages (ps:[ps.pygame ps.pillow ps.atomicwrites ps.svgwrite]))
    pkgs.zlib
  ];
  LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc pkgs.zlib ];
  FONT_PATH = pkgs.lib.makeSearchPathOutput "out" "share/fonts/noto" [ pkgs.noto-fonts ];

}

