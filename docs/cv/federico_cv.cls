\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{federico_cv}[custom CV class]
\LoadClass{article}
\RequirePackage{titlesec}
\usepackage[letterpaper, bottom=0.75in, top=1in, footnotesep=2em]{geometry}
\usepackage{float}
\usepackage[dvipsnames]{xcolor}

\usepackage[multiple,symbol]{footmisc}

\usepackage{fontspec}
\setmainfont{HelveticaNeue}

\definecolor{dark}{RGB}{0, 0, 0}

\usepackage[colorlinks = true,
            linkcolor = dark,
            urlcolor  = dark,
            citecolor = dark,
            anchorcolor = dark]{hyperref}

\usepackage[normalem]{ulem}
\setlength{\ULdepth}{2pt}

\newcommand{\link}[2]{\href{#1}{\dashuline{\smash{#2}}}}

\usepackage{fancyhdr}

% \usepackage{showframe} % good for debugging

\pagestyle{fancy}
\fancyhf{}
\usepackage{lastpage}
\rhead{\thepage/\pageref{LastPage}}
\renewcommand{\headrulewidth}{0pt}
\setlength{\headheight}{0in}

\thispagestyle{empty}
\usepackage{multirow}
\usepackage{tabularx}
\newcommand{\contact}[3]{
\vfill\noindent
\begin{tabularx}{\linewidth}{@{}Xr@{}}
  \multirow{2}{*}{\textbf{\huge{#1}}} & #2\\
                                      & #3
\end{tabularx}
\vspace{0em}
}

\usepackage{longtable}

\titleformat{\section}
  {\large}
  {}{0em}
  {}
  [\titlerule]

\titleformat{\subsection}
  {\normalsize}
  {}{0em}
  {}
  [\titlerule]

\newenvironment{halfTblSubSection}[3]
    {
    \begin{minipage}[t]{0.45\linewidth}
    \begin{longtable}{@{}p{#2\linewidth} p{#3\linewidth}}
        \multicolumn{2}{@{}p{\linewidth}}{#1} \\
        \cline{1-2} \\
    }
    {
    \end{longtable}
    \end{minipage}
    }

\newenvironment{tblSection}[3]
    {
    \section{#1}
    \vspace{-1em}
    \begin{longtable}{@{}p{#2\linewidth} p{#3\linewidth} }
    }
    {
    \end{longtable}
    }

\newenvironment{tblSubSection}[3]
    {
    \subsection{#1}
    \vspace{-1em}
    \begin{longtable}{@{}p{#2\linewidth} p{#3\linewidth} }
    }
    {
    \end{longtable}
    }

\newcommand{\leftbfrightsmallleftright}[2]{#1 & \textbf{#2}\\\leftbfrightsmallleftrightCheckNextArg}
\newcommand{\leftbfrightsmallleftrightCheckNextArg}{\@ifnextchar\bgroup{\leftbfrightsmallleftrightGobbleNextArg}{\\[-0.6em]}}
\newcommand{\leftbfrightsmallleftrightGobbleNextArg}[2]{\footnotesize{#1} & #2\\\@ifnextchar\bgroup{\leftbfrightsmallleftrightGobbleNextArg}{\\[-0.6em]}}

\newcommand{\bfsingledash}[1]{\textbf{#1} & \\\bfsingledashCheckNextArg}
\newcommand{\bfsingledashCheckNextArg}{\@ifnextchar\bgroup{\bfsingledashGobbleNextArg}{\\[-0.6em]}}
\newcommand{\bfsingledashGobbleNextArg}[1]{\hspace{\parindent} - #1 & \\\@ifnextchar\bgroup{\bfsingledashGobbleNextArg}{\\[-0.6em]}}

\newcommand{\singledash}[1]{#1 & \\\singledashCheckNextArg}
\newcommand{\singledashCheckNextArg}{\@ifnextchar\bgroup{\singledashGobbleNextArg}{\\[-0.6em]}}
\newcommand{\singledashGobbleNextArg}[1]{\hspace{\parindent} - #1 & \\\@ifnextchar\bgroup{\singledashGobbleNextArg}{\\[-0.6em]}}

\newcommand{\leftbfrightsingle}[2]{%
    #1 & \textbf{#2} \\\leftbfrightsingleCheckNextArg}
\newcommand{\leftbfrightsingleCheckNextArg}{\@ifnextchar\bgroup{\leftbfrightsingleGobbleNextArg}{\\[-0.6em]}}
\newcommand{\leftbfrightsingleGobbleNextArg}[1]{& #1 \\\@ifnextchar\bgroup{\leftbfrightsingleGobbleNextArg}{\\[-0.6em]}}

\newcommand{\leftrightsingle}[2]{%
    #1 & #2 \\\leftrightsingleCheckNextArg}
\newcommand{\leftrightsingleCheckNextArg}{\@ifnextchar\bgroup{\leftrightsingleGobbleNextArg}{\\[-0.6em]}}
\newcommand{\leftrightsingleGobbleNextArg}[1]{& #1 \\\@ifnextchar\bgroup{\leftrightsingleGobbleNextArg}{\\[-0.6em]}}

\newcommand{\leftrightsingletight}[2]{%
    #1 & #2 \\\leftrightsingletightCheckNextArg}
\newcommand{\leftrightsingletightCheckNextArg}{\@ifnextchar\bgroup{\leftrightsingletightGobbleNextArg}{\\[-1em]}}
\newcommand{\leftrightsingletightGobbleNextArg}[1]{& #1 \\\@ifnextchar\bgroup{\leftrightsingletightGobbleNextArg}{\\[-1em]}}

\newcommand{\leftbfrightsingletight}[2]{%
    #1 & \textbf{#2} \\\leftbfrightsingletightCheckNextArg}
\newcommand{\leftbfrightsingletightCheckNextArg}{\@ifnextchar\bgroup{\leftbfrightsingletightGobbleNextArg}{\\[-1em]}}
\newcommand{\leftbfrightsingletightGobbleNextArg}[1]{& #1 \\\@ifnextchar\bgroup{\leftbfrightsingletightGobbleNextArg}{\\[-1em]}}

\newcommand{\students}[2]{%
    #1 & \textbf{#2} \\\studentsCheckNextArg}
\newcommand{\studentsCheckNextArg}{\@ifnextchar\bgroup{\studentsGobbleNextArg}{\\[-1em]}}
\newcommand{\studentsGobbleNextArg}[1]{& #1 \\\@ifnextchar\bgroup{\studentsGobbleNextArg}{\\[-0.65em]}}

\newcommand{\degree}{\leftbfrightsingle}
\newcommand{\job}{\leftbfrightsingle}
\newcommand{\service}{\bfsingledash}
\newcommand{\talk}{\singledash}
\newcommand{\award}{\leftrightsingletight}
\newcommand{\grant}{\leftbfrightsingle}