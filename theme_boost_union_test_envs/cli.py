"""Console script for theme_boost_union_test_envs."""

import fire


def help() -> None:
    print("theme_boost_union_test_envs")
    print("=" * len("theme_boost_union_test_envs"))
    print('Test environments for the Moodle theme "Boost Union"')


def main() -> None:
    fire.Fire({"help": help})


if __name__ == "__main__":
    main()  # pragma: no cover
