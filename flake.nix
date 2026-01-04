{
  description = "abstractcp - Create abstract class variables";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python312;
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            python
            pkgs.python310
            pkgs.python311
            pkgs.python312
            pkgs.python313
            pkgs.python314
            pkgs.git
          ];

          shellHook = ''
            if [ ! -d .venv ]; then
              echo "Creating virtual environment..."
              ${python}/bin/python -m venv .venv
            fi

            source .venv/bin/activate

            echo "Installing package with dev dependencies..."
            python -m pip install --upgrade pip
            python -m pip install -e ".[dev]"

            if [ -z "$ZSH_VERSION" ]; then
              exec zsh
            fi
          '';
        };
      }
    );
}
