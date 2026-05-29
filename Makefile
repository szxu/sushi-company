.PHONY: test doctor

test:
	bash tests/smoke.sh

doctor:
	bin/doctor
