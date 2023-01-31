(TeX-add-style-hook "pracMNUB"
 (lambda ()
    (TeX-add-symbols
     "TitreRapport"
     "DateRapport"
     "AuteurRapport"
     "NomEntreprise")
    (TeX-run-style-hooks
     "latex2e"
     "art12"
     "article"
     "a4paper"
     "12pt"
     "style/packages"
     "style/newcommands"
     "style/style"
     "title/title"
     "body/pages/introduction"
     "body/pages/titre1/titre1"
     "body/pages/titre2/titre2")))

