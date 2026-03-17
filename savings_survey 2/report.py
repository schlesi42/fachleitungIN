import os
import textwrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def generate_pdf(questions, output_path="output/report.pdf"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with PdfPages(output_path) as pdf:
        for question in questions:
            n = question.num_axes
            if n == 2:
                fig, axes = plt.subplots(
                    1, 2, figsize=(16, 7),
                    gridspec_kw={'width_ratios': [2, 1]}
                )
                axes_list = list(axes)
            else:
                fig, ax = plt.subplots(1, 1, figsize=(10, 6))
                axes_list = [ax]

            wrapped_title = textwrap.fill(question.question_text, width=100)
            fig.suptitle(wrapped_title, fontsize=10, y=0.98, va='top')
            fig.subplots_adjust(top=0.80, bottom=0.15, left=0.08, right=0.97)

            question.visualize(axes_list)

            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)

    print(f"Report gespeichert: {output_path}")
