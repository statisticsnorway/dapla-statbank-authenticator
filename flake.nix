{
  description = "dapla-statbank-authenticator ";

  inputs = {
    flake-parts.url = "github:hercules-ci/flake-parts";
    nixpkgs.url = "github:NixOS/nixpkgs?ref=nixpkgs-unstable";
  };

  outputs = inputs @ {flake-parts, ...}:
    flake-parts.lib.mkFlake {inherit inputs;} {
      systems = ["x86_64-linux" "aarch64-linux" "aarch64-darwin" "x86_64-darwin"];
      perSystem = {
        config,
        self',
        inputs',
        pkgs,
        system,
        ...
      }: {
        devShells.default = pkgs.mkShell {
          name = "statbank-authenticator";

          packages = with pkgs; [
            bump2version
            poetry
            python313
            ruff
            uv
            yaml-language-server
          ];
        };

        formatter = pkgs.alejandra;
      };
    };
}
