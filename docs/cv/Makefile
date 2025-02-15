PROJECT = cv

default: build/$(PROJECT).pdf

view: default
	(${OPEN} $(PROJECT).pdf &)

### Compilation Flags
PDFLATEX_FLAGS  = -shell-escape -halt-on-error -output-directory build/

### Standard PDF Viewers
UNAME := $(shell uname)

ifeq ($(UNAME), Linux)
OPEN = xdg-open
endif

ifeq ($(UNAME), Darwin)
OPEN = open
endif

### Pushing
push:
	scp cv.pdf login.eecs.berkeley.edu:public_html/cv.pdf

### Clean
clean:
	rm -rf build/

### Core Latex Generation
build/: clean
	mkdir -p build/

build/$(PROJECT).aux: build/
	xelatex $(PDFLATEX_FLAGS) $(PROJECT)

build/$(PROJECT).bbl: build/$(PROJECT).aux
	biber build/$(PROJECT)
	xelatex $(PDFLATEX_FLAGS) $(PROJECT)
	
build/$(PROJECT).pdf: build/$(PROJECT).aux build/$(PROJECT).bbl
	xelatex $(PDFLATEX_FLAGS) $(PROJECT)
	cp build/cv.pdf cv.pdf
