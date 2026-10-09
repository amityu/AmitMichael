from pathlib import Path

from fpdf import FPDF


OUTPUT_DIR = Path("../resources")

MM_PER_INCH = 25.4
DEFAULT_MIN_GAP_BETWEEN_CORES = 2.5
DEFAULT_MIN_GAP_BETWEEN_CIRCLES = 2.5
TWO_CORE_EDGE_OFFSET = 1.5

PT_TO_MM = MM_PER_INCH / 72
MAX_DETAILS_FONT_SIZE = 12
MIN_DETAILS_FONT_SIZE = 4
DETAILS_LINE_SPACING = 1.5


class RotaryDieCanvas:
    def __init__(
        self,
        die_width,
        cylinder_perimeter,
        cores_number,
        core_width,
        diameter,
        z=64,
        min_gap_between_cores=DEFAULT_MIN_GAP_BETWEEN_CORES,
        min_gap_between_circles=DEFAULT_MIN_GAP_BETWEEN_CIRCLES,
    ):
        self.die_width = die_width
        self.cylinder_perimeter = cylinder_perimeter
        self.cores_number = cores_number
        self.core_width = core_width
        self.diameter = diameter
        self.z = z
        self.min_gap_between_cores = min_gap_between_cores
        self.min_gap_between_circles = min_gap_between_circles

        self.grid = []
        self.properties = ""

    @property
    def pdf_size(self):
        return self.core_width * self.cores_number, self.cylinder_perimeter

    @property
    def gap_between_cores(self):
        if self.cores_number == 1:
            return 0

        return self.min_gap_between_cores

    def calculate_grid(self):
        self.grid = []

        circles_per_core_line = self._calculate_circles_per_core_line()
        edge_distance = self._calculate_edge_distance(circles_per_core_line)
        y_gap = self._calculate_y_gap()

        y = y_gap / 2

        while y < self.cylinder_perimeter:
            for core_index in range(self.cores_number):
                x = self._first_circle_x(core_index, edge_distance)

                for _ in range(circles_per_core_line):
                    self.grid.append((x, y))
                    x += self.diameter + self.min_gap_between_circles

            y += y_gap

        self.properties = self._build_properties(circles_per_core_line, edge_distance)

    def save_circle_grid_pdf(self, file_name):
        self._ensure_grid_is_ready()

        pdf = self._create_pdf()
        self._add_details_page(pdf)
        self._add_circle_grid_page(pdf)

        self._save_pdf(pdf, file_name)

    def save_backslit_pdf(self, file_name):
        self._ensure_grid_is_ready()

        pdf = self._create_pdf()
        self._add_details_page(pdf)
        self._add_backslit_page(pdf)

        self._save_pdf(pdf, file_name)

    def save_ring_grid_pdf(self, inner_diameter, file_name):
        self._ensure_grid_is_ready()

        pdf = self._create_pdf()
        self._add_details_page(pdf, extra_details=f"Inner diameter = {inner_diameter:.2f} mm\n")
        self._add_ring_grid_page(pdf, inner_diameter)

        self._save_pdf(pdf, file_name)

    def _calculate_circles_per_core_line(self):
        available_width = (
            self.core_width
            - self.gap_between_cores
            - self.min_gap_between_circles
        )

        circle_pitch = self.diameter + self.min_gap_between_circles

        return int(available_width / circle_pitch)

    def _calculate_edge_distance(self, circles_per_core_line):
        used_width = circles_per_core_line * (
            self.diameter + self.min_gap_between_circles
        )

        return (self.core_width + self.min_gap_between_circles - used_width) / 2

    def _calculate_y_gap(self):
        rows_count = int(
            self.cylinder_perimeter
            / (self.diameter + self.min_gap_between_circles)
        )

        return self.cylinder_perimeter / rows_count

    def _first_circle_x(self, core_index, edge_distance):
        x = edge_distance + self.diameter / 2 + core_index * self.core_width

        if self.cores_number == 2 and core_index == 0:
            x -= edge_distance - TWO_CORE_EDGE_OFFSET

        if self.cores_number == 2 and core_index == 1:
            x += edge_distance - TWO_CORE_EDGE_OFFSET

        return x

    def _build_properties(self, circles_per_core_line, edge_distance):
        total_circles = len(self.grid)
        efficiency = (circles_per_core_line / self.core_width) * 100
        length_per_1000_per_core = self.cylinder_perimeter / (
            total_circles / self.cores_number
        )
        circles_span = self._calculate_circles_span()

        properties = (
            "Internal information\n"
            f"Circle diameter = {self.diameter:.2f} mm\n"
            f"Cylinder perimeter = {self.cylinder_perimeter:.2f} mm\n"
            f"Number of {self.core_width:.2f} mm cores = {self.cores_number}\n"
            f"Number of circles in 1 core line = {circles_per_core_line}\n"
            f"Edge distance = {edge_distance:.2f} mm\n"
            f"In between cores distance = {self.gap_between_cores:.2f} mm\n"
            f"In between circles distance = {self.min_gap_between_circles:.2f} mm\n"
            f"Leftmost to rightmost circle edge = {circles_span:.2f} mm\n"
            f"Number of circles = {total_circles}\n"
            f"Length of 1000 pcs/core = {length_per_1000_per_core:.2f} m\n"
            f"Precision = {efficiency:.2f}\n"
        )

        if self.cores_number == 2:
            properties += (
                f"2 cores, circles were offset by "
                f"{edge_distance - TWO_CORE_EDGE_OFFSET:.2f} mm\n"
            )

        return properties

    def _calculate_circles_span(self):
        if not self.grid:
            return 0

        x_values = [x for x, _ in self.grid]

        return max(x_values) - min(x_values) + self.diameter

    def _create_pdf(self):
        return FPDF(format=self.pdf_size)

    def _add_details_page(self, pdf, extra_details=""):
        pdf.add_page()

        text = (self.properties + extra_details).rstrip("\n")
        lines = text.split("\n")

        text_width = pdf.w - pdf.l_margin - pdf.r_margin
        text_height = pdf.h - pdf.t_margin - pdf.b_margin

        font_size = MAX_DETAILS_FONT_SIZE
        while font_size > MIN_DETAILS_FONT_SIZE:
            pdf.set_font("helvetica", "B", font_size)
            line_height = font_size * PT_TO_MM * DETAILS_LINE_SPACING
            widest_line = max(pdf.get_string_width(line) for line in lines)

            fits_height = len(lines) * line_height <= text_height
            fits_width = widest_line + 2 * pdf.c_margin <= text_width
            if fits_height and fits_width:
                break

            font_size -= 0.5

        pdf.multi_cell(text_width, line_height, text, border="L", align="L")

    def _add_circle_grid_page(self, pdf):
        pdf.add_page()

        for x, y in self.grid:
            self._draw_circle(pdf, x, y, self.diameter)

    def _add_backslit_page(self, pdf):
        pdf.add_page()

        for x in sorted({x for x, _ in self.grid}):
            pdf.line(x, 0, x, self.cylinder_perimeter)

    def _add_ring_grid_page(self, pdf, inner_diameter):
        pdf.add_page()

        for x, y in self.grid:
            self._draw_circle(pdf, x, y, self.diameter)
            self._draw_circle(pdf, x, y, inner_diameter)

    @staticmethod
    def _draw_circle(pdf, center_x, center_y, diameter):
        radius = diameter / 2

        pdf.ellipse(
            x=center_x - radius,
            y=center_y - radius,
            w=diameter,
            h=diameter,
            style="D",
        )

    def _save_pdf(self, pdf, file_name):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        pdf.output(str(OUTPUT_DIR / file_name))

    def _ensure_grid_is_ready(self):
        if not self.grid:
            self.calculate_grid()


def build_output_file_name(diameter, z, cores_number, core_width, material):
    return f"D{diameter * 100:.0f}Z{z}-C{cores_number}X{core_width}{material}28.pdf"


if __name__ == "__main__":
    die_perimeter = 8 * MM_PER_INCH
    core_number = 2
    core_width = 68
    material = "GF"
    z = 64

    for diameter in [29]:
        canvas = RotaryDieCanvas(
            die_width=core_width * core_number,
            cylinder_perimeter=die_perimeter,
            cores_number=core_number,
            core_width=core_width,
            diameter=diameter,
            z=z,
        )

        canvas.calculate_grid()

        canvas.save_circle_grid_pdf(
            build_output_file_name(
                diameter=diameter,
                z=z,
                cores_number=core_number,
                core_width=core_width,
                material=material,
            )
        )