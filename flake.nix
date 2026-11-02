{
  description = "dapla-statbank-authenticator dev environment";

  inputs = {
    flake-parts.url = "github:hercules-ci/flake-parts";
    nixpkgs.url = "https://channels.nixos.org/nixpkgs-unstable/nixexprs.tar.zst";
  };

  outputs = inputs @ {flake-parts, ...}:
    flake-parts.lib.mkFlake {inherit inputs;} {
      systems = ["x86_64-linux" "aarch64-linux" "aarch64-darwin"];
      perSystem = {pkgs, ...}: {
        devShells.default = pkgs.mkShell {
          name = "statbank-authenticator";

          packages = with pkgs; [
            bump2version
            docker-language-server
            nixd
            python313
            ruff
            trivy
            uv
            yaml-language-server
          ];
        };

        formatter = pkgs.alejandra;
      };
    };
}
