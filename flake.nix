{
  description = "Tiny Tapeout SKY130 local hardening environment";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { nixpkgs, ... }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in {
      devShells = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
        in {
          default = pkgs.mkShell {
            packages = with pkgs; [
              python312
              uv
              git
              docker-client
              gnumake
              iverilog
              gtkwave
              librsvg
              pngquant
            ];

            LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath (with pkgs; [
              stdenv.cc.cc.lib
              zlib
              expat
              cairo
              libpng
              qhull
            ]);

            shellHook = ''
              export PDK_ROOT="''${PDK_ROOT:-$PWD/.ttsetup/pdk}"
              export PDK="''${PDK:-sky130A}"
              export LIBRELANE_TAG="''${LIBRELANE_TAG:-3.0.14}"
              export UV_PYTHON_DOWNLOADS=never

              tt-setup() {
                uv venv --python ${pkgs.python312}/bin/python .venv || return
                uv pip install --python .venv/bin/python \
                  -r tt/requirements.txt \
                  -r test/requirements.txt \
                  "librelane==$LIBRELANE_TAG" || return
                source .venv/bin/activate
              }

              if [ -f .venv/bin/activate ]; then
                source .venv/bin/activate
              fi
              echo "Tiny Tapeout: run tt-setup once to install Python dependencies."
            '';
          };
        });
    };
}
