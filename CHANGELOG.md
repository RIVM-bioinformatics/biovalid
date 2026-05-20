# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0](https://github.com/RIVM-bioinformatics/biovalid/compare/biovalid-v0.3.0...biovalid-v0.4.0) (2025-12-30)


### Features

* add VCF validation and improve testing ([057962e](https://github.com/RIVM-bioinformatics/biovalid/commit/057962e862be98534b60b0d1078a461f251937af))

## [0.3.0](https://github.com/RIVM-bioinformatics/biovalid/compare/biovalid-v0.2.0...biovalid-v0.3.0) (2025-09-03)


### Features

* add .bai support ([e03987b](https://github.com/RIVM-bioinformatics/biovalid/commit/e03987b2223928bbf51025b41027fffe19e5f7df))
* added GFF and BAI checking to biovalid ([52e1968](https://github.com/RIVM-bioinformatics/biovalid/commit/52e19682558390a1ddd8e283bbc65ba6cb8f0758))
* added GFF checking to biovalid ([99486fa](https://github.com/RIVM-bioinformatics/biovalid/commit/99486fa24cc6620c1a4aff1fa0d0e6cc7b460024))


### CI/CD

* renamed file in workflow ([3281b59](https://github.com/RIVM-bioinformatics/biovalid/commit/3281b59764730fba77dc8b0d0de7fe0b73dcc45e))

## [0.2.0](https://github.com/RIVM-bioinformatics/biovalid/compare/biovalid-v0.1.0...biovalid-v0.2.0) (2025-08-27)


### Features

* first working version ([cb28d74](https://github.com/RIVM-bioinformatics/biovalid/commit/cb28d74e9d8ce4e7d61204eb4dc2e34b89de9c16))
* first working version ([7175758](https://github.com/RIVM-bioinformatics/biovalid/commit/71757585969b2e1337bc74f1d18061bb0768b577))


### Bug Fixes

* included windows line endings in fasta validator ([c676bb5](https://github.com/RIVM-bioinformatics/biovalid/commit/c676bb520544b3bf97031dd317cf275bccd9ebdf))
* move workflow to correct position ([3b5105b](https://github.com/RIVM-bioinformatics/biovalid/commit/3b5105b75d56ac7957441f887d7f63a670e75729))


### Documentation

* Update README.md ([ab20a40](https://github.com/RIVM-bioinformatics/biovalid/commit/ab20a401f3720f78fbbeba0c2e83eab512f62dad))


### CI/CD

* added tests into release-please workflow ([b52544c](https://github.com/RIVM-bioinformatics/biovalid/commit/b52544cc0b6fbc61c06f7197506f368ed8aa6f58))
* removed test pypi thing ([82fea19](https://github.com/RIVM-bioinformatics/biovalid/commit/82fea1961a51b8044482d48f15247d496b2382f6))
* update docstring e2e cli test ([136c239](https://github.com/RIVM-bioinformatics/biovalid/commit/136c23969e93ac10a62d6474971dcdb645df16e0))
* update docstring test_unit ([a1d4dba](https://github.com/RIVM-bioinformatics/biovalid/commit/a1d4dba2503a134874f7939f0edf020eacab93da))
* update docstring test_unit ([ab63e6b](https://github.com/RIVM-bioinformatics/biovalid/commit/ab63e6be18b529acc305a67045c37552ae36d7a0))

## [Unreleased]

### Added
- Initial release of biovalid package
- Validators for various genomic file formats (BAM, FASTA, FASTQ)
- Command-line interface for file validation
- Comprehensive test suite
