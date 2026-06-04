.PHONY: test unit bdd bdd-vanilla bdd-vanilla-linux doctor

test: unit bdd

unit:
	bash tests/smoke.sh

bdd:
	npm run bdd

bdd-vanilla:
	bash tests/bdd-vanilla.sh

bdd-vanilla-linux:
	bash tests/bdd-vanilla-linux.sh

doctor:
	bin/doctor
