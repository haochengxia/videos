from manimlib import *
import itertools as it

def box_line(row, l_idx, r_idx, h, squeeze=0.0):
    
    buff = 0.2
    obj_height = row[0].get_height()
    obj_width = row[0].get_width()
    buff += obj_height / 2
    l_x, r_x = row[l_idx].get_x() - obj_width / 2 + squeeze, row[r_idx].get_x() + obj_width / 2 - squeeze
    y = row[l_idx].get_y()
    
    ll = Line([l_x , y + buff], [l_x, y + h], color=YELLOW)
    ll.set_stroke(width=6)
    tl = Line([l_x - 0.03, y + h], [r_x + 0.03, y + h], color=YELLOW)
    tl.set_stroke(width=6)
    rl = Line([r_x, y + h], [r_x, y + buff], color=YELLOW)
    rl.set_stroke(width=6)
    return VGroup(ll, tl, rl)

def count_prefix_matching(t1, t2):
    for i in range(len(t1)):
        if t1[i] != t2[i]:
            return i
    return len(t1)


def get_row_shift(top_row, low_row, n):
    min_index = low_row[0].index
    max_index = top_row[-1].index
    max_sum = min_index + max_index
    if n <= max_sum:
        x_shift = top_row[n - 2 * min_index].get_x() - low_row[0].get_x()
    else:
        x_shift = top_row[-1].get_x() - low_row[n - max_sum].get_x()
    return low_row.animate.shift(x_shift * RIGHT)

def get_top_row_shift(top_row, low_row, n):
    max_sum = low_row[-1].index
    if n <= max_sum:
        x_shift = low_row[n].get_x() - top_row[0].get_x()
    else:
        x_shift = low_row[[-1]].get_x() - top_row[0].get_x()
    return top_row.animate.shift(x_shift * RIGHT)


def get_aligned_pairs(group1, group2, n):
    return VGroup(*(
        VGroup(m1, m2)
        for m1 in group1
        for m2 in group2
        if m1.index + m2.index == n
    ))


def get_comp_pairs(group1, group2, m):
    return VGroup(*(
        VGroup(group1[i], group2[i])
        for i in range(m)
    ))


# Introduction

class SimpleExample(Scene):
    def construct(self):
        run_time_base = 0.5
        text = "baabacababad"
        pattern = "aba"
        n = len(text)
        m = len(pattern)
        two_string = Tex("\\text{Text}\\ T:\\ \\texttt{baabacababad}\\quad \\text{Pattern}\\ P:\\ \\texttt{aba}")
        question = Tex("\\text{Find all occurrences of}\\ P\\ \\text{in}\\ T")
        two_string[4:5].set_color(BLUE)
        two_string[25:26].set_color(RED)
        question[20:21].set_color(BLUE)
        question[23:24].set_color(RED)
        group = VGroup(two_string, question)
        group.arrange(DOWN)
        group.to_edge(UP)
        self.play(Write(two_string, run_time=1.5), FadeIn(question, 0.5 * DOWN, time_span=(0.5, 1.5)))
        self.wait()

        text_row = Square(side_length=0.75).get_grid(1, 12, buff=0)
        pattern_row = Square(side_length=0.75).get_grid(1, 3, buff=0)
        for row, values in (text_row, list(text)), (pattern_row, list(pattern)):
            for index, value, square in zip(it.count(), values, row):
                value_label = Tex("\\texttt{" + value + "}")
                value_label.move_to(square)
                square.value_label = value_label
                square.add(value_label)
                square.value = value
                square.index = index
        VGroup(text_row, pattern_row).arrange(RIGHT, buff=LARGE_BUFF)

        self.play(
            TransformFromCopy(two_string[6:18:1].copy(), text_row),  # TransformMatchingShapes
            TransformFromCopy(two_string[27:30:1].copy(), pattern_row),
        )
        self.wait()

        # Set up position
        text_row.generate_target()
        pattern_row.generate_target()
        text_row.target.center()
        pattern_row.target.next_to(text_row.target, DOWN, MED_LARGE_BUFF)
        pattern_row.target.align_to(text_row.target, LEFT)

        self.play(LaggedStart(
            MoveToTarget(text_row),
            MoveToTarget(pattern_row),  # path_arc=PI
            FadeOut(question, UP),
        ))
        self.wait()

        # March!
        for i in range(n - m + 1):
            same_cnt = count_prefix_matching(text[i:i + m], pattern)
            comp_cnt = min(same_cnt + 1, m)
            self.play(get_row_shift(text_row, pattern_row, i), run_time=run_time_base)
            pairs = get_comp_pairs(text_row[i:i + m], pattern_row, m)
            label_pairs = VGroup(*(
                VGroup(m1.value_label, m2.value_label)
                for m1, m2 in pairs
            ))
            # new_label_pairs = label_pairs.copy()
            # compare each char
            rects = VGroup(*(
                SurroundingRectangle(lp, buff=0.2).set_stroke(YELLOW, 1).round_corners()
                for lp in label_pairs[:comp_cnt]
            ))
            r_text_row = VGroup(*[text_row[j].copy() for j in range(i, i + comp_cnt)])
            # for j in range(comp_cnt):
            #     if j <= same_cnt:
            #         r_text_row[j].set_stroke(color=GREEN, width=DEFAULT_STROKE_WIDTH)
            #     else:
            #         r_text_row[j].set_stroke(color=RED, width=DEFAULT_STROKE_WIDTH) 
            r_text_row[:same_cnt].set_fill(GREEN, opacity=0.5)
            r_text_row[same_cnt:comp_cnt].set_fill(RED, opacity=0.5)

            self.play(
                # FadeIn(rects, lag_ratio=0.5),
                Write(r_text_row, lag_ratio=0.5, run_time=run_time_base / 2 * comp_cnt)
            )  # lag_ratio - sub obj latency
            self.wait()
            # for j in range(comp_cnt):
            #     r_text_row[j].set_stroke(color=WHITE, width=DEFAULT_STROKE_WIDTH)
            # r_text_row.set_fill(BLACK, opacity=0.5) 

            if same_cnt == m:
                success_match = VGroup(*[text_row[j].value_label for j in range(i, i + m)])
                rect = SurroundingRectangle(success_match, buff=0.25 if i == 8 else 0.2) \
                    .set_stroke(YELLOW, 2).round_corners()  # small patch for overlapping
                self.play(FadeIn(rect, run_time=run_time_base))
            self.play(
                # FadeOut(rects),
                FadeOut(r_text_row, run_time=run_time_base)
            )
            self.wait()


class SameCharExample(Scene):
    def construct(self):
        run_time_base = 0.5
        case1 = Tex("\\text{If all characters in pattern}\\ P\\ \\text{are the same}",
                    t2c={"same": ORANGE})
        case1[24:25].set_color(RED)

        text = "aaxxaaaaax"
        pattern = "aaaa"
        n = len(text)
        m = len(pattern)
        two_string = Tex("\\text{Text}\\ T:\\ \\texttt{aaxxaaaaax}\\quad \\text{Pattern}\\ P:\\ \\texttt{aaaa}")
        two_string[4:5].set_color(BLUE)
        two_string[23:24].set_color(RED)

        group = VGroup(case1, two_string)
        group.arrange(DOWN)
        group.to_edge(UP)
        self.play(Write(case1, run_time=1.5), FadeIn(two_string, 0.5 * DOWN, time_span=(0.5, 1.5)))
        text_row = Square(side_length=0.75).get_grid(1, 10, buff=0)
        pattern_row = Square(side_length=0.75).get_grid(1, 4, buff=0)
        for row, values in (text_row, list(text)), (pattern_row, list(pattern)):
            for index, value, square in zip(it.count(), values, row):
                value_label = Tex("\\texttt{" + value + "}")
                value_label.move_to(square)
                square.value_label = value_label
                square.add(value_label)
                square.value = value
                square.index = index
        VGroup(text_row, pattern_row).arrange(RIGHT, buff=LARGE_BUFF)

        self.play(
            TransformFromCopy(two_string[6:16:1].copy(), text_row),
            TransformFromCopy(two_string[25:29:1].copy(), pattern_row),
        )
        self.wait()

        # Set up position
        text_row.generate_target()
        pattern_row.generate_target()
        text_row.target.center()
        pattern_row.target.next_to(text_row.target, DOWN, MED_LARGE_BUFF)
        pattern_row.target.align_to(text_row.target, LEFT)

        self.play(LaggedStart(
            MoveToTarget(text_row),
            MoveToTarget(pattern_row)
        ))
        self.wait()

        # March!
        i = 0
        old_r_text_row = None
        old_r_text_row_4 = None  # index 4
        while i <= n - m:
            same_cnt = count_prefix_matching(text[i:i + m], pattern)
            comp_cnt = min(same_cnt + 1, m)
            self.play(get_row_shift(text_row, pattern_row, i), run_time=run_time_base)
            r_text_row = VGroup(*[text_row[j].copy() for j in range(i, i + comp_cnt)])
            r_text_row[:same_cnt].set_fill(GREEN, opacity=0.5)
            r_text_row[same_cnt:comp_cnt].set_fill(RED, opacity=0.5)
            self.play(
                Write(r_text_row if (i != 5 and i != 6) else r_text_row[-1], lag_ratio=0.5,
                      run_time=run_time_base / 2 * comp_cnt)
            )  # lag_ratio - sub obj latency
            self.wait()
            if same_cnt == m:
                success_match = VGroup(*[text_row[j].value_label for j in range(i, i + m)])
                rect = SurroundingRectangle(success_match, buff=0.25 if i == 5 else 0.2) \
                    .set_stroke(YELLOW, 2).round_corners()  # small patch for overlapping
                self.play(FadeIn(rect, run_time=run_time_base))
            if i <= 4:
                self.play(
                    FadeOut(r_text_row if i != 4 else r_text_row[0], run_time=run_time_base)
                )
                old_r_text_row_4 = r_text_row
            elif i == 5:
                self.play(
                    FadeOut(old_r_text_row[1], run_time=run_time_base),
                )
            else:
                self.play(
                    FadeOut(old_r_text_row_4[2:], run_time=run_time_base),
                    FadeOut(old_r_text_row[-1], run_time=run_time_base),
                    FadeOut(r_text_row[-1], run_time=run_time_base),
                )
            self.wait()
            if comp_cnt != same_cnt:
                i += comp_cnt
            else:
                i += 1
            old_r_text_row = r_text_row

        # Add analysis
        braces = VGroup(
            Brace(two_string[6:16], DOWN),
            Brace(two_string[25:29], DOWN),
        )

        for brace, text in zip(braces, ["n = 10", "m = 4"]):
            brace.words = brace.get_tex(f"{text}")
        for brace in braces:
            self.play(
                GrowFromCenter(brace),
                FadeIn(brace.words, 0.25 * UP)
            )
            self.wait()

        complexity = Tex("\\text{The number of comparisons:}\\ 10 \\rightarrow O(n)")
        complexity.to_edge(DOWN)
        self.play(Write(complexity, run_time=1.5))
        self.wait()


class DiffCharExample(Scene):
    def construct(self):
        run_time_base = 0.5
        case2 = Tex("\\text{If all characters in pattern}\\ P\\ \\text{are different}",
                    t2c={"different": ORANGE})
        case2[24:25].set_color(RED)
        text = "abcdababcd"
        pattern = "abcd"
        n = len(text)
        m = len(pattern)
        two_string = Tex("\\text{Text}\\ T:\\ \\texttt{abcdababcd}\\quad \\text{Pattern}\\ P:\\ \\texttt{abcd}")
        two_string[4:5].set_color(BLUE)
        two_string[23:24].set_color(RED)
        group = VGroup(case2, two_string)
        group.arrange(DOWN)
        group.to_edge(UP)
        self.play(Write(case2, run_time=1.5), FadeIn(two_string, 0.5 * DOWN, time_span=(0.5, 1.5)))
        text_row = Square(side_length=0.75).get_grid(1, 10, buff=0)
        pattern_row = Square(side_length=0.75).get_grid(1, 4, buff=0)
        for row, values in (text_row, list(text)), (pattern_row, list(pattern)):
            for index, value, square in zip(it.count(), values, row):
                value_label = Tex("\\texttt{" + value + "}")
                value_label.move_to(square)
                square.value_label = value_label
                square.add(value_label)
                square.value = value
                square.index = index
        VGroup(text_row, pattern_row).arrange(RIGHT, buff=LARGE_BUFF)

        self.play(
            TransformFromCopy(two_string[6:16:1].copy(), text_row),
            TransformFromCopy(two_string[25:29:1].copy(), pattern_row),
        )
        self.wait()

        # Set up position
        text_row.generate_target()
        pattern_row.generate_target()
        text_row.target.center()
        pattern_row.target.next_to(text_row.target, DOWN, MED_LARGE_BUFF)
        pattern_row.target.align_to(text_row.target, LEFT)

        self.play(LaggedStart(
            MoveToTarget(text_row),
            MoveToTarget(pattern_row)
        ))
        self.wait()

        # March!
        i = 0
        while i <= n - m:
            same_cnt = count_prefix_matching(text[i:i + m], pattern)
            comp_cnt = min(same_cnt + 1, m)
            self.play(get_row_shift(text_row, pattern_row, i), run_time=run_time_base)
            r_text_row = VGroup(*[text_row[j].copy() for j in range(i, i + comp_cnt)])
            r_text_row[:same_cnt].set_fill(GREEN, opacity=0.5)
            r_text_row[same_cnt:comp_cnt].set_fill(RED, opacity=0.5)
            self.play(
                Write(r_text_row, lag_ratio=0.5, run_time=run_time_base / 2 * comp_cnt)
            )
            self.wait()
            if same_cnt == m:
                success_match = VGroup(*[text_row[j].value_label for j in range(i, i + m)])
                rect = SurroundingRectangle(success_match, buff=0.25 if i == 5 else 0.2) \
                    .set_stroke(YELLOW, 2).round_corners()  # small patch for overlapping
                self.play(FadeIn(rect, run_time=run_time_base))
            self.play(
                FadeOut(r_text_row, run_time=run_time_base)
            )
            self.wait()
            i += same_cnt

        # Add analysis
        braces = VGroup(
            Brace(two_string[6:16], DOWN),
            Brace(two_string[25:29], DOWN),
        )

        for brace, text in zip(braces, ["n = 10", "m = 4"]):
            brace.words = brace.get_tex(f"{text}")
        for brace in braces:
            self.play(
                GrowFromCenter(brace),
                FadeIn(brace.words, 0.25 * UP)
            )
            self.wait()
        m_text = Tex("\\text{matching} + \\text{non-matching}",
                     t2c={"matching": GREEN, "non-matching": RED})
        complexity = Tex("\\text{The number of comparisons:}\\ 10+1 \\rightarrow O(n)")
        complexity[23:25].set_color(GREEN)
        complexity[26:27].set_color(RED)
        group = VGroup(m_text, complexity)
        group.arrange(DOWN)
        group.to_edge(DOWN)

        self.play(Write(complexity, run_time=1.5),
                  Write(m_text, run_time=1.5),
                  )
        self.wait()


class Recall(Scene):
    def construct(self):
        run_time_base = 1
        title = Tex("\\text{\\underline{Recall the frist example}}")
        text = "baabacababad"
        pattern = "aba"
        n = len(text)
        m = len(pattern)
        title.to_corner(UL, buff=MED_SMALL_BUFF)
        self.play(Write(title))

        competition = SVGMobject(
            "/root/manim/raster/cup.svg",
            color=YELLOW,
            stroke_width=2
        )
        competition.scale(0.5)
        competition.to_corner(UR, buff=MED_SMALL_BUFF)
        self.play(FadeIn(competition))

        alice = Tex('\\text{Alice}', font_size=48)
        alice_text_row = Square(side_length=0.75).get_grid(1, 12, buff=0)
        alice_pattern_row = Square(side_length=0.75).get_grid(1, 3, buff=0)
        for row, values in (alice_text_row, list(text)), (alice_pattern_row, list(pattern)):
            for index, value, square in zip(it.count(), values, row):
                value_label = Tex("\\texttt{" + value + "}")
                value_label.move_to(square)
                square.value_label = value_label
                square.add(value_label)
                square.value = value
                square.index = index
        alice_grp = VGroup(alice_text_row, alice_pattern_row).arrange(RIGHT)

        bob = Tex('\\text{Bob}', font_size=48)
        bob_text_row = Square(side_length=0.75).get_grid(1, 12, buff=0)
        bob_pattern_row = Square(side_length=0.75).get_grid(1, 3, buff=0)
        for row, values in (bob_text_row, list(text)), (bob_pattern_row, list(pattern)):
            for index, value, square in zip(it.count(), values, row):
                value_label = Tex("\\texttt{" + value + "}")
                value_label.move_to(square)
                square.value_label = value_label
                square.add(value_label)
                square.value = value
                square.index = index

        bob_grp = VGroup(bob_text_row, bob_pattern_row).arrange(RIGHT)

        ns_grp = VGroup(alice, alice_grp, bob, bob_grp).arrange(DOWN, buff=LARGE_BUFF)
        self.play(FadeIn(alice),
                  FadeIn(alice_text_row),
                  FadeIn(alice_pattern_row),
                  FadeIn(bob),
                  FadeIn(bob_text_row),
                  FadeIn(bob_pattern_row),
                  )
        self.wait()

        r_alice_pattern_row = alice_pattern_row.copy()
        r_alice_text_row = alice_text_row.copy()
        r_bob_pattern_row = bob_pattern_row.copy()
        r_bob_text_row = bob_text_row.copy()

        r_alice_pattern_row.set_fill(RED, opacity=0.5)
        r_alice_text_row.set_fill(BLUE, opacity=0.5)
        r_bob_pattern_row.set_fill(RED, opacity=0.5)
        r_bob_text_row.set_fill(BLUE, opacity=0.5)

        self.play(
            FadeIn(r_alice_pattern_row),
            FadeIn(r_alice_text_row),
            FadeIn(r_bob_pattern_row),
            FadeIn(r_bob_text_row),
        )

        self.play(
            FadeOut(r_alice_pattern_row),
            FadeOut(r_alice_text_row),
            FadeOut(r_bob_pattern_row),
            FadeOut(r_bob_text_row),
        )

        for o in [alice, alice_text_row, alice_pattern_row, bob, bob_text_row, bob_pattern_row]:
            o.generate_target()
        # alice.to_edge(LEFT)
        # alice_text_row.target.center()
        alice_pattern_row.target.next_to(alice_text_row.target, DOWN)
        alice_pattern_row.target.align_to(alice_text_row.target, LEFT)
        alice.target.next_to(alice_text_row.target, UP)
        alice.target.align_to(alice_text_row.target, LEFT)

        # bob.to_edge(LEFT)
        bob_pattern_row.target.next_to(bob_text_row.target, DOWN)
        bob_pattern_row.target.align_to(bob_text_row.target, LEFT)
        bob.target.next_to(bob_text_row.target, UP)
        bob.target.align_to(bob_text_row.target, LEFT)
        # r_alice_pattern_row = alice_pattern_row.copy()
        # r_alice_text_row = alice_text_row.copy()
        # r_bob_pattern_row = bob_pattern_row.copy()
        # r_bob_text_row = bob_text_row.copy()

        # r_alice_pattern_row.set_fill(RED, opacity=0.5)
        # r_alice_text_row.set_fill(BLUE, opacity=0.5)        
        # r_bob_pattern_row.set_fill(RED, opacity=0.5)
        # r_bob_text_row.set_fill(BLUE, opacity=0.5)

        self.play(LaggedStart(
            MoveToTarget(alice),
            MoveToTarget(alice_text_row),
            MoveToTarget(alice_pattern_row),
            MoveToTarget(bob),
            MoveToTarget(bob_text_row),
            MoveToTarget(bob_pattern_row),

        ))
        self.play(ns_grp.animate.shift(UP),
                  )
        self.wait()

        # March!
        old_same_cnt = 0
        i = 0
        ra_trs, rb_trs = dict(), dict()
        while i < n - m:
            if old_same_cnt >= 2:
                i += 1
            same_cnt = count_prefix_matching(text[i:i + m], pattern)
            comp_cnt = min(same_cnt + 1, m)
            self.play(get_row_shift(alice_text_row, alice_pattern_row, i),
                      get_row_shift(bob_text_row, bob_pattern_row, i),
                      run_time=run_time_base)
            old_same_cnt = same_cnt

            ra_text_row = VGroup(*[alice_text_row[j].copy() for j in range(i, i + comp_cnt)])
            rb_text_row = VGroup(*[bob_text_row[j].copy() for j in range(i, i + comp_cnt)])

            ra_trs[str(i)] = ra_text_row
            rb_trs[str(i)] = rb_text_row

            ra_text_row[:same_cnt].set_fill(GREEN, opacity=0.5)
            ra_text_row[same_cnt:comp_cnt].set_fill(RED, opacity=0.5)
            rb_text_row[:same_cnt].set_fill(GREEN, opacity=0.5)
            rb_text_row[same_cnt:comp_cnt].set_fill(RED, opacity=0.5)

            if i == 4:
                # Bob say 
                bob_say = Tex("\\text{: I can avoid comparing with this}\\ \\texttt{a} \\text{!}", font_size=48)
                bob_say.next_to(bob, RIGHT)
                self.play(Write(bob_say))
                self.play(Uncreate(bob_say))

            self.play(
                Write(ra_text_row, lag_ratio=0.5, run_time=run_time_base / 2 * comp_cnt),
                Write(rb_text_row[1:] if i in [4, 8] else rb_text_row,
                      lag_ratio=0.5, run_time=run_time_base / 2 * comp_cnt),
            )

            # if i in [2, 6, 8]:

            if same_cnt == m:
                a_success_match = VGroup(*[alice_text_row[j].value_label for j in range(i, i + m)])
                b_success_match = VGroup(*[bob_text_row[j].value_label for j in range(i, i + m)])
                a_rect = SurroundingRectangle(a_success_match, buff=0.25 if i == 8 else 0.2) \
                    .set_stroke(YELLOW, 2).round_corners()
                b_rect = SurroundingRectangle(b_success_match, buff=0.25 if i == 8 else 0.2) \
                    .set_stroke(YELLOW, 2).round_corners()
                self.play(FadeIn(a_rect, run_time=run_time_base))
                self.play(FadeIn(b_rect, run_time=run_time_base))

            if i == 4:
                self.play(
                    FadeOut(ra_text_row, run_time=run_time_base),
                    FadeOut(rb_text_row[1:2], run_time=run_time_base),
                    FadeOut(rb_trs['2'][-1:], run_time=run_time_base),
                )
            elif i == 8:
                self.play(
                    FadeOut(ra_text_row, run_time=run_time_base),
                    FadeOut(rb_text_row[1:], run_time=run_time_base),
                    FadeOut(rb_trs['6'][-1:], run_time=run_time_base),
                )
            else:
                self.play(
                    FadeOut(ra_text_row, run_time=run_time_base),
                    FadeOut(rb_text_row[:2] if i in [2, 6] else rb_text_row, run_time=run_time_base),
                )
            self.wait()

            if i == 2:
                # Alice say
                alice_say = Tex("\\text{: I can skip the next shift!}", font_size=48)
                alice_say.next_to(alice, RIGHT)
                self.play(Write(alice_say))
                self.play(Uncreate(alice_say))

            i += 1
        # r_competition = competition.copy()
        competition.generate_target()
        competition.target.scale(0.3).next_to(bob, RIGHT)
        # competition.target.align_to(bob_text_row.target, TOP)

        alice_compare = Tex("\\text{15 comparisons}")
        bob_compare = Tex("\\text{13 comparisons}")
        alice_compare.next_to(alice_text_row, RIGHT)
        bob_compare.next_to(bob_text_row, RIGHT)

        self.play(MoveToTarget(competition),
                  Write(alice_compare),
                  Write(bob_compare)
                  )
        self.wait()

        lingo = Tex("\\text{{\\textbf{\\textit{Preprocessing}} then \\textbf{\\textit{Search}}}}",
                    t2c={"Preprocessing": ORANGE})
        lingo.to_edge(UL, buff=MED_SMALL_BUFF)
        self.play(ReplacementTransform(title, lingo))
        self.wait()

        self.clear()
        self.wait()


def get_grid_rows(row, color=GREY_B, stroke_width=2):
    height = width = get_norm(row[1].get_center() - row[0].get_center())
    return VGroup(*[
        Rectangle(
            height=height,
            width=width,
            stroke_color=color,
            stroke_width=stroke_width,
        ).move_to(bit)
        for bit in row
    ])



class Preprocessing(Scene):
    """ Fundamental preprocessing of the pattern """

    def construct(self):
        run_time_base = 0.5
        lingo = Tex("\\text{\\underline{Fundamental preprocessing}}",
                    t2c={"pre-processing": ORANGE})
        lingo.to_edge(UL, buff=MED_SMALL_BUFF)
        self.play(Write(lingo))
        self.wait()

        answer = Tex("\\text{: compute}\\ Z\\ \\text{values}")
        answer.next_to(lingo, RIGHT)

        s = "aabcaabxaaa"
        s_tex = Tex("\\text{String}\\ S\\ \\texttt{aabcaabxaaa}")
        s_tex[6:7].set_color(ORANGE)

        # Row
        s_row = Square(side_length=0.75).get_grid(1, 11, buff=0)
        for index, value, square in zip(it.count(), list(s), s_row):
            value_label = Tex("\\texttt{" + value + "}")
            value_label.move_to(square)
            square.value_label = value_label
            square.add(value_label)
            square.value = value
            square.index = index

        s_row.generate_target()
        # s_row.target.space_out_submobjects(1.2)
        s_row.target.center()
        s_row.target.scale(1.2)

        new_boxes = get_grid_rows(s_row.target, color=GREY_B)
        # h_buff = get_norm(s_row.target[0].get_center() - s_row.target[4].get_center())
        # for box in new_boxes:
        #     box.set_height(h_buff, stretch=True)
        # Position in each box
        p_labels = VGroup()
        for i, box in enumerate(new_boxes):
            label = Integer(i+1)  # position
            label.set_height(0.15)
            label.set_color(YELLOW)
            label.move_to(box, DR)
            label.shift(SMALL_BUFF * UL)
            p_labels.add(label)

        self.play(MoveToTarget(s_row), FadeIn(p_labels, lag_ratio=0.07, run_time=3))
        self.wait()
        

        r_s_row = s_row.copy()
        
        for square in r_s_row:
            square.set_stroke(BLACK)
            
        r_s_row.next_to(s_row, UP)
        zbox = Tex("Z\\text{-}box")
        zbox.next_to(r_s_row, LEFT)
        self.play(TransformFromCopy(s_row.copy(), r_s_row))
        
        z_values = [0]
        for i in range(1, len(s)):
            z_values.append(count_prefix_matching(s[i:], s))
        z_row = Square(side_length=0.75 * 1.2).get_grid(1, 11, buff=0)
        z_row.next_to(s_row, DOWN)
        for index, square in zip(it.count(), z_row):
            value_label = Integer(z_values[index])
            value_label.set_height(0.3)
            value_label.set_color(BLUE)
            value_label.move_to(square)
            square.value_label = value_label
            square.add(value_label)
            square.index = index
            square.set_stroke(BLACK)
        
        z = Tex("Z")
        z.next_to(z_row, LEFT)
        self.play(Write(z))
        self.wait()
        
        self.play(FadeIn(z_row[0]))
        
        for i in range(1, len(s)):
            self.play(get_top_row_shift(r_s_row, s_row, i),
                      run_time=run_time_base)
            
            rr_s_row = s_row.copy()
            if z_values[i] == len(s) - i:
                rr_s_row[i:].set_fill(GREEN, opacity=0.5)
            else:
                rr_s_row[i:i+z_values[i]].set_fill(GREEN, opacity=0.5)
                rr_s_row[i+z_values[i]].set_fill(RED, opacity=0.5)
                
            self.play(FadeIn(rr_s_row[i:i+z_values[i]]))
            self.play(FadeIn(z_row[i]),
                      FadeOut(rr_s_row))
            self.wait()
        

        
        self.play(FadeIn(zbox),
                  FadeOut(r_s_row))

        # Z boxes
        zbox_lines = dict()
        for i in range(len(s)):
            if z_values[i] != 0:
                lines = box_line(s_row, i, i+z_values[i]-1, 
                                 1.6 if i in [5, 9] else (1.2 if i == 10 else 2), 
                                 squeeze=0.2 if i == 10 else 0.0)
                zbox_lines[str(i+1)] = lines
                self.play(Write(lines), lag_ratio=0.7)
                
        self.wait()
            
        # Show R i and L i
        r = Tex("R")
        l = Tex("L")
        r_row = Square(side_length=0.75 * 1.2).get_grid(1, 11, buff=0)
        l_row = Square(side_length=0.75 * 1.2).get_grid(1, 11, buff=0)
        r_row.next_to(z_row, DOWN)
        l_row.next_to(r_row, DOWN)
        r.next_to(r_row, LEFT)
        l.next_to(l_row, LEFT)
        
        r_values = [-1, 2, -1, -1, 7, 7, 7, -1, 10, 11, 11]
        l_values = [-1, 2, -1, -1, 5, 5, 5, -1, 9, 10, 10]  # last 10 or 11
        for index, z_value in enumerate(z_values):
            if z_value != 0:
                pass
        
    def add_block_labels(self, blocks, letter, color=BLUE, font_size=30):
        labels = VGroup()
        for n, square in enumerate(blocks):
            label = Tex(f"{letter}_{{{n}}}", font_size=font_size)
            label.set_color(color)
            label.next_to(square, UP, SMALL_BUFF)
            square.label = label
            square.add(label)
            labels.add(label)
        return labels
    
    
        # 
        # We need something to guide us, Sure that's Z-value

        # We can a little bit transform the problem put the pattern before the text, Then we got a string S

        # Why we can reuse, the character is repeated, if we now find one can, the repeat also
        # And the diffrent help us find the repeat more quickly

        # Then if we put this idea into the text, 


class Z4Matching(Scene):
    """ Z-Algorithm """

    def construct(self):
        pass

# # TODO
# class BMAlgo(Scene):
#     """ Boyer-Moore Algorithm """
#     def construct(self):
#         pass

# # TODO
# class KMPAlgo(Scene):
#     """ Knuth-Morris-Pratt Algorithm"""
#     def construct(self):
#         pass
