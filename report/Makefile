LATEXMK ?= latexmk
SOURCE := report.tex

.PHONY: all clean

all:
	$(LATEXMK) -pdf $(SOURCE)

clean:
	$(LATEXMK) -C $(SOURCE)
	rm -rf latex_build
