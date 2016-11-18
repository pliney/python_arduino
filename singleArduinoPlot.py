import serial
import numpy as np
from time import time
from pprint import pprint as pp
from random import randint

def initialize(**kwargs):
    clear(**kwargs)

def clear(plot, **kwargs):
    plot.clear()

    plot.set_plot_properties(
        title='Time Series',
        x_label='Time',
        y_label='Position',
        x_scale='linear',
        y_scale='linear',
        aspect_ratio='auto')
    plot.new_curve('ts', memory='growable', animated=True,
                     line_color='green')

def run(plot, stop, messages, **kwargs):
    global data
    print('starting')
    ser = serial.Serial('COM4', 9600)

    s = ser.readline() #read a line before plotting, w/o this the readline
                       # would sometimes start in the middle of a data line

    start_time = time()
    i = 0
    complete_x_list = []
    times = []
    x_accel_list = []
    rolling_array_size = 20
    for j in range(0, rolling_array_size):
        s = ser.readline()

        x_accel = float(s)
        x_accel_list.append(x_accel)

    while True:
        s = ser.readline()
        x_accel = float(s)

        #add newest item to list and delete oldest item from list
        x_accel_list.append(x_accel)
        del x_accel_list[0]

        t1 = time()
        # messages.write('Time: %f\n' % (start_time - t1))
        # times.append('Time: %f' % (t1 - start_time))
        times.append((t1 - start_time))
        complete_x_list.append(np.mean(x_accel_list))

        plot.append_data('ts', [(t1 - start_time), np.mean(x_accel_list)])


        '''Updates plot every 5 data reads instead of every data reads,
        could be useful if we have performance issues'''
        # plot_x.append_data('ts',[(t1 - start_time),np.mean(x_accel_list)],redraw=False)
        # if (i % 5) == 0:
        #     plot_x.append_data('ts', [(t1 - start_time), np.mean(x_accel_list)])

        i += 1

        '''Timing: prints to console the time taken for each iteration and the average of every 100 iterations'''
        # if (i % 100) == 0:
        #     time_diffs = [j - i for i, j in zip(times[:-1], times[1:])]
        #     pp(time_diffs)
        #     print(np.mean(time_diffs))
        #     times = []
        #     i = 0

        if stop.value:
            data = (times, complete_x_list)
            break
    stop.value = False



def plot_guess(function, fit_type, initial_guess, messages, plot, **kwargs):
    global data
    xs = data[0]
    ys = data[1]
    initial_fit_parameters = np.array(eval(initial_guess.value))
    # the function we are trying to fit to the data
    function_string = function.value
    def f(x, *p):
        y = eval(function_string)
        plot.set_data('fit', np.column_stack((x, y)))
        return y
    f(xs, *initial_fit_parameters)


def fit(function, fit_type, initial_guess, messages, plot, **kwargs):
    global data
    xs = data[0]
    ys = data[1]

    initial_fit_parameters = np.array(eval(initial_guess.value))
    # the function we are trying to fit to the data
    function_string = function.value
    def f(x, *p):
        y = eval(function_string)
        plot.set_data('fit', np.column_stack((x, y)))
        return y
    # the actual fitting
    if fit_type.value == 'linear':
        A = np.column_stack([xs, np.ones(len(xs))])
        m, c = np.linalg.lstsq(A, ys)[0]
        messages.write('slope = %g, intercept = %g\n' % (m, c))
        plot.set_data('fit', np.column_stack((xs, m*xs+c)))
    else:
        plot.set_data('fit', np.column_stack((xs, f(xs, *initial_fit_parameters))))
        fit, cov = scipy.optimize.curve_fit(f, xs, ys, p0=initial_fit_parameters)
        plot.set_data('fit', np.column_stack((xs, f(xs, *fit))), rescale=True)
        messages.write('Fit p = %s.\n' % str(fit))
        messages.write('Uncertainties eps = %s.\n' % str(np.sqrt(np.diag(cov))))





    ser.close()

    # print(xaxis)
    # messages.write('The average acceleraion is: %f  %d' % (np.average(xaxis), 5))
