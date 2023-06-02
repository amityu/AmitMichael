from fpdf import FPDF
from scipy.optimize import minimize
import numpy as np

OUTPUT_PATH = '../resources/'


class canvas:
    def __init__(self, die_width,cylinder_perimeter, cores_number,
                 core_width, diameter):
        self.cylinder_perimeter =cylinder_perimeter
        self.cores_number = cores_number
        self.cores_width = core_width
        self.die_width = die_width
        self.diameter = diameter
        self.y_inbetween = 2.8

    def set_grid(self):
        self.grid = []

        # x[0] inbetweem discs x[1] edges
        def n(x):
            return -int((x[0] + self.cores_width - 2 * x[1]) / (d + x[0]))

        d = self.diameter

        bounds = ((2.5, self.cores_width), (1.5, self.cores_width))
        res = minimize(n, (2.5, 1.5), bounds=bounds)
        number_of_discs = -n(res.x)
        edge_distance = res.x[1]
        in_distance = res.x[0]  #distance of float number of discs
        inbetween = (self.cores_width - 2 * edge_distance - number_of_discs * d) / (number_of_discs - 1)

        self.properties = 'Circle diameter %.2f\n'%d
        self.properties += 'cylinder perimeter %.2f mm\n'%self.cylinder_perimeter
        self.properties += 'die width = %.2f\n'%self.die_width
        self.properties += 'number of %.2f mm cores =  %d \n'%(self.cores_width,self.cores_number)
        self.properties += 'number of labels in 1 core line= %d\n' % number_of_discs
        self.properties +='edge distance = %.2f\n' % edge_distance
        self.properties +='in between distance = %.2f\n' % inbetween
        print( 'Precision = %.02f' % ((number_of_discs / self.cores_width) * 100))
        dd = {'diameter': d, 'dia_inch': d / 25.4, 'core': self.cores_width, 'label_number': number_of_discs,
                      'edge': edge_distance, 'in_between': inbetween,
                      'efficiency': (number_of_discs / self.cores_width) * 100}

        y_gap = self.cylinder_perimeter/int(self.cylinder_perimeter/(self.diameter + 2.5))
        count = 0
        y = y_gap/2
        while y< self.cylinder_perimeter:
            for core in range(self.cores_number):
                x = edge_distance + self.diameter / 2 + core * self.cores_width

                for disc in range(number_of_discs):
                    self.grid.append((x,y))
                    x+= d + inbetween
            y +=  y_gap

        self.properties += 'number of circles = %d'%len(self.grid)


    def draw_shape_on_grid(self,shape):
        print()
    def save_canvas(self):
        pdf = FPDF(format = (self.die_width,self.cylinder_perimeter))
        pdf.add_page();
        pdf.set_font('Arial', 'B', 12);
        pdf.multi_cell(100, 15, self.properties, border='L', align ='L');
        pdf.add_page()
        for (x,y) in self.grid:
            pdf.ellipse(x=x-self.diameter/2, y=y-self.diameter/2, w=self.diameter, h=self.diameter, style="D")
        pdf.output(OUTPUT_PATH + "sample4.pdf")
        print()

class shape:
    def __init__(self):
        print()
    def draw(self):
        print()


c  =canvas(114, 8*25.4,3,38, 4)
c.set_grid()
c.save_canvas()
















