pkgname = "bear"
pkgver = "4.2.0"
pkgrel = 0
build_style = "cargo"
hostmakedepends = ["cargo-auditable"]
makedepends = ["rust-std"]
pkgdesc = "Generate compile_commands.json for any C or C++ build"
license = "GPL-3.0-or-later"
url = "https://github.com/rizsotto/Bear"
source = f"https://github.com/rizsotto/Bear/archive/refs/tags/{pkgver}.tar.gz"
sha256 = "711fc941bb124f802236c6e7e87f60118b005d0b9efaeb601cbd5b178c5d2fd3"


def post_build(self):
    triplet = self.profile().triplet
    self.do(
        f"target/{triplet}/release/generate-completions",
        f"target/{triplet}/release/completions",
    )


def init_check(self):
    self.do("cargo", "build", "--target", self.profile().triplet)


def install(self):
    src_dir = f"target/{self.profile().triplet}/release"

    self.install_file(f"{src_dir}/bear-driver", "usr/lib/bear/bin", mode=0o755)
    self.install_file(f"{src_dir}/bear-wrapper", "usr/lib/bear/bin", mode=0o755)

    if (self.cwd / f"{src_dir}/libexec.so").exists():
        self.install_file(
            f"{src_dir}/libexec.so", "usr/lib/bear/lib", mode=0o755
        )

    bin_dir = self.destdir / "usr/bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    wrapper_path = bin_dir / "bear"
    wrapper_path.write_text(
        """#!/bin/sh
exec /usr/lib/bear/bin/bear-driver "$@"
"""
    )
    wrapper_path.chmod(0o755)

    if (self.cwd / "man/bear.1").exists():
        self.install_man("man/bear.1")

    comp_dir = f"{src_dir}/completions"
    if (self.cwd / f"{comp_dir}/bear.bash").exists():
        self.install_completion(f"{comp_dir}/bear.bash", "bash")
        self.install_completion(f"{comp_dir}/bear.fish", "fish")
        self.install_completion(f"{comp_dir}/_bear", "zsh")
