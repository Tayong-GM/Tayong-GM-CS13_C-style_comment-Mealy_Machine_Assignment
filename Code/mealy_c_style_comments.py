"""
Mealy machine for C-style block comments: /* ... */

Alphabet: a = any character except '*' or '/'
Output: 1 only when the transition completes the closing delimiter */.
The input is accepted only if it ends immediately after that transition.

Install matplotlib if needed:
    py -m pip install matplotlib
Run:
    py mealy_c_style_comments.py
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch

TRANSITIONS = {
    "q0": {"a": ("qD", "0"), "*": ("qD", "0"), "/": ("q1", "0")},
    "q1": {"a": ("qD", "0"), "*": ("q2", "0"), "/": ("qD", "0")},
    "q2": {"a": ("q2", "0"), "*": ("q3", "0"), "/": ("q2", "0")},
    "q3": {"a": ("q2", "0"), "*": ("q3", "0"), "/": ("q4", "1")},
    "q4": {"a": ("qD", "0"), "*": ("qD", "0"), "/": ("qD", "0")},
    "qD": {"a": ("qD", "0"), "*": ("qD", "0"), "/": ("qD", "0")},
}

def classify(text):
    state = "q0"
    outputs, states = [], [state]
    for symbol in text:
        if symbol not in {"a", "*", "/"}:
            raise ValueError(f"Invalid symbol {symbol!r}; use only a, *, /.")
        state, output = TRANSITIONS[state][symbol]
        outputs.append(output)
        states.append(state)
    accepted = bool(outputs) and outputs[-1] == "1" and state == "q4"
    return accepted, "".join(outputs), states

def draw_graph(filename="mealy_c_style_comments_graph.png"):
    pos = {
        "q0": (0, 1), "q1": (2, 1), "q2": (4, 1),
        "q3": (6, 1), "q4": (8.5, 1), "qD": (4, -1.5)
    }
    labels = {
        "q0": "q0\\nStart", "q1": "q1\\nSaw /",
        "q2": "q2\\nInside comment", "q3": "q3\\nSaw * inside",
        "q4": "q4\\nACCEPT", "qD": "qD\\nDEAD / REJECT"
    }
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(-1.2, 10.2); ax.set_ylim(-2.6, 3); ax.axis("off")
    ax.set_title("Mealy Machine for C-style Block Comments", fontsize=16, pad=16)

    for s, (x, y) in pos.items():
        color = "#d9f2df" if s == "q4" else "#f8dada" if s == "qD" else "#e5efff"
        r = .52
        ax.add_patch(Circle((x, y), r, facecolor=color, edgecolor="#25324a", lw=1.6))
        if s == "q4":
            ax.add_patch(Circle((x, y), r-.09, fill=False, edgecolor="#25324a", lw=1.2))
        ax.text(x, y, labels[s], ha="center", va="center", fontsize=9)

    def edge(src, dst, label, rad=0, color="#34445e", start=None, end=None, label_xy=None):
        x1, y1 = pos[src]; x2, y2 = pos[dst]
        if start is None:
            dx, dy = x2-x1, y2-y1
            norm = (dx*dx+dy*dy)**.5 or 1
            start = (x1 + dx/norm*.52, y1 + dy/norm*.52)
            end = (x2 - dx/norm*.52, y2 - dy/norm*.52)
        patch = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=13,
                                lw=1.35, color=color,
                                connectionstyle=f"arc3,rad={rad}")
        ax.add_patch(patch)
        if label_xy is None:
            label_xy = ((start[0]+end[0])/2, (start[1]+end[1])/2 + .22)
        ax.text(*label_xy, label, fontsize=9, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=.18", fc="white", ec="none", alpha=.95))

    ax.annotate("", xy=(-.53, 1), xytext=(-1, 1),
                arrowprops=dict(arrowstyle="-|>", lw=1.5, color="#34445e"))
    ax.text(-1, 1.25, "START", fontsize=9)

    edge("q0", "q1", "/ / 0", label_xy=(1, 1.32))
    edge("q1", "q2", "* / 0", label_xy=(3, 1.32))
    edge("q2", "q3", "* / 0", label_xy=(5, 1.32))
    edge("q3", "q4", "/ / 1", label_xy=(7.25, 1.35))

    # Self-loops: q2 stays inside on ordinary characters or slash; q3 stays
    # on another star; a non-star inside q3 returns to q2.
    for s, lab, yoff in [("q2", "a, / / 0", .95), ("q3", "* / 0", .95)]:
        x, y = pos[s]
        patch = FancyArrowPatch((x-.28, y+.43), (x+.28, y+.43),
                                connectionstyle="arc3,rad=-1.25",
                                arrowstyle="-|>", mutation_scale=12, lw=1.25,
                                color="#34445e")
        ax.add_patch(patch)
        ax.text(x, y+1.05, lab, fontsize=8.5, ha="center")
    # q3 --a/0--> q2, curved back edge
    edge("q3", "q2", "a / 0", rad=-.42, label_xy=(5, .1))

    # Invalid paths from opening states and any character after acceptance.
    edge("q0", "qD", "a, * / 0", rad=.08, color="#a33",
         start=(-.12, .48), end=(3.55, -1.18), label_xy=(1.25, -.2))
    edge("q1", "qD", "a, / / 0", rad=0, color="#a33",
         start=(1.85, .48), end=(3.75, -1.0), label_xy=(2.8, -.35))
    edge("q4", "qD", "a, *, / / 0", rad=.15, color="#a33",
         start=(8.2, .5), end=(4.55, -1.05), label_xy=(7.0, -.25))

    # Dead-state loop
    x, y = pos["qD"]
    patch = FancyArrowPatch((x-.28, y-.42), (x+.28, y-.42),
                            connectionstyle="arc3,rad=-1.25",
                            arrowstyle="-|>", mutation_scale=12, lw=1.25,
                            color="#a33")
    ax.add_patch(patch)
    ax.text(x, y-1.02, "a, *, / / 0", fontsize=8.5, ha="center")

    ax.text(4.5, -2.35,
            "Transition label = input / output     |     a = any character except * or /",
            fontsize=10, ha="center")
    fig.tight_layout()
    fig.savefig(filename, dpi=180, bbox_inches="tight")
    plt.show()

def main():
    print("MEALY MACHINE: C-STYLE BLOCK COMMENTS")
    print("Alphabet: a = ordinary character, '*' = star, '/' = slash")
    print("Output 1 marks the transition that completes */.")
    print("ACCEPT only if the input ends immediately after that transition.\n")
    tests = [
        "/*a*/", "/*/", "/**/", "/*a**/", "/*aaa*aaa*/",
        "/*", "/**", "*/", "/*a", "/*a*//", "//aaaa"
    ]
    print(f"{'INPUT':<15}{'OUTPUT TRACE':<16}{'RESULT':<10}STATE TRACE")
    print("-" * 95)
    for sample in tests:
        accepted, outputs, states = classify(sample)
        print(f"{sample:<15}{outputs or '(empty)':<16}"
              f"{'ACCEPT' if accepted else 'REJECT':<10}{' -> '.join(states)}")
    draw_graph()

if __name__ == "__main__":
    main()
