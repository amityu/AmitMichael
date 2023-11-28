from fpdf import FPDF
from scipy.optimize import minimize
import numpy as np

OUTPUT_PATH = '../resources/'

class canvas:
    def __init__(self, die_width,cylinder_perimeter, cores_number,
                 core_width, diameter, Z=64):
        self.cylinder_perimeter =cylinder_perimeter
        self.cores_number = cores_number
        self.cores_width = core_width
        self.die_width = die_width
        self.diameter = diameter
        self.y_inbetween = 2.5

    def set_grid(self):
        # minimizing number was removed, you can just take calculate the max number of discs and place spaces where
        #necessary

        self.grid = []

        # x[0] inbetweem discs x[1] edges
        #def n(x):
        #    return -int((x[0] + self.cores_width - 2 * x[1]) / (d + x[0]))

        d = self.diameter


        '''
        #inbetween distance optimization
        bounds = ((2.5, self.cores_width), (2.25, self.cores_width))
        res = minimize(n, (2.5, 2.5), bounds=bounds)
        number_of_discs = -n(res.x)
        edge_distance = res.x[1]
        in_distance = res.x[0]  #distance of float number of discs
        inbetween = (self.cores_width - 2 * edge_distance - number_of_discs * d) / (number_of_discs - 1)
        '''
        minimum_inbetween_cores = 4
        minimum_inbetween_discs = 2.5
        number_of_discs = int((self.cores_width -minimum_inbetween_cores+minimum_inbetween_discs)/(self.diameter + minimum_inbetween_discs))
        edge_distance = (self.cores_width + minimum_inbetween_discs - number_of_discs*(self.diameter +minimum_inbetween_discs))/2
        self.properties = 'Circle diameter %.2f\n'%d
        self.properties += 'cylinder perimeter %.2f mm\n'%self.cylinder_perimeter
        #self.properties += 'die width = %.2f\n'%self.die_width
        self.properties += 'number of %.2f mm cores =  %d \n'%(self.cores_width,self.cores_number)
        self.properties += 'number of labels in 1 core line= %d\n' % number_of_discs
        self.properties +='edge distance = %.2f\n' % edge_distance
        self.properties += 'in between cores distance = %.2f\n' % minimum_inbetween_cores
        if self.cores_number == 2 :
            self.properties += '2 cores,discs were offseted by %.02f mm \n' % (edge_distance - 1.5)
        self.properties +='in between discs distance = %.2f\n' % minimum_inbetween_discs

        print( 'Precision = %.02f' % ((number_of_discs / self.cores_width) * 100))
        dd = {'diameter': d, 'dia_inch': d / 25.4, 'core': self.cores_width, 'label_number': number_of_discs,
                      'edge': edge_distance, 'in_between_discs': minimum_inbetween_discs, 'in_between_cores': minimum_inbetween_cores,
                      'efficiency': (number_of_discs / self.cores_width) * 100}

        y_gap = self.cylinder_perimeter/int(self.cylinder_perimeter/(self.diameter + 2.5))
        count = 0
        y = y_gap/2
        while y< self.cylinder_perimeter:
            for core in range(self.cores_number):

                x = edge_distance + self.diameter / 2 + core * self.cores_width
                if self.cores_number == 2 and core == 0:
                    x -= edge_distance -1.5

                if self.cores_number ==2 and core ==1:
                    x += edge_distance -1.5

                for disc in range(number_of_discs):
                    self.grid.append((x,y))
                    x+= d +minimum_inbetween_discs
            y +=  y_gap

        self.properties += 'number of circles = %d \n'%len(self.grid)
        self.properties += 'length of 1000pcs/core  = %.02f m \n '% (self.cylinder_perimeter / (len(self.grid) /self.cores_number))



    def draw_shape_on_grid(self,shape):
        print()
    def save_canvas(self,file_name):
        pdf = FPDF(format = (self.cores_width*self.cores_number,self.cylinder_perimeter))
        pdf.add_page();
        pdf.set_font('Arial', 'B', 12);
        pdf.multi_cell(100, 15, self.properties, border='L', align ='L');
        pdf.add_page()
        for (x,y) in self.grid:
            pdf.ellipse(x=x-self.diameter/2, y=y-self.diameter/2, w=self.diameter, h=self.diameter, style="D")
        pdf.output(OUTPUT_PATH + file_name)
        print()
    def backslit(self, file_name):
        pdf = FPDF(format=(self.cores_width * self.cores_number, self.cylinder_perimeter))
        pdf.add_page();
        pdf.set_font('Arial', 'B', 12);

        pdf.multi_cell(100, 15, self.properties, border='L', align='L');
        pdf.add_page()
        xset = set()
        for (x, y) in self.grid:
            xset.add(x)
        for x in xset:
            pdf.line(x,0,x, self.cylinder_perimeter)
        pdf.output(OUTPUT_PATH + file_name)
        print()
    def ring(self, inner_diameter,file_name):
        self.properties += 'Inner Diameter = %d \n' % inner_diameter


        pdf = FPDF(format=(self.cores_width * self.cores_number, self.cylinder_perimeter))
        pdf.add_page();
        pdf.set_font('Arial', 'B', 12);
        pdf.multi_cell(100, 15, self.properties, border='L', align='L');
        pdf.add_page()
        for (x, y) in self.grid:
            pdf.ellipse(x=x - self.diameter / 2, y=y - self.diameter / 2, w=self.diameter, h=self.diameter,
                        style="D")
            pdf.ellipse(x=x - inner_diameter / 2, y=y - inner_diameter / 2, w=inner_diameter, h=inner_diameter,
                        style="D")
        pdf.output(OUTPUT_PATH + file_name)
        print()
class shape:
    def __init__(self):
        print()
    def draw(self):
        print()


#die_width =114
die_perimeter = 8*25.4
core_number =1
core_width = 120
material ='GF'
in_dia = 6.35
Z=64

for diameter in [36]:

    c  =canvas(core_width*core_number, die_perimeter,core_number,core_width, diameter,Z)
    c.set_grid()
    c.save_canvas(OUTPUT_PATH + "D%dZ%d-C%dX%d%s28.pdf"%(diameter*100,Z,core_number,core_width,material))
    #c.backslit(OUTPUT_PATH + "BS_D%dZ%d-C%dX%d%s.pdf"%(diameter*100,Z,core_number,core_width,material))
    #c.ring(in_dia,OUTPUT_PATH + "R%dd%dZ%d-C%dX%d%s.pdf"%(diameter*100,in_dia*100,Z,core_number,core_width,material))



















#%%
