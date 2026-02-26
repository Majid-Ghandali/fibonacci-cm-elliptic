name: fibonacci-cm-elliptic
channels:
  - conda-forge
  - defaults
dependencies:
  # نسخه پایتون را اینجا برداشتم تا ورک‌فلو بتواند ماتریکس را اعمال کند
  - numpy
  - scipy
  - pandas
  - matplotlib
  - pytest
  - pytest-cov 
  - mypy
  - flake8
  - pip
  - pip:
      - twine
      - build
