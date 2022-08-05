import numpy as np
#import matplotlib.pyplot as plt
import xlwings as xw
import Adams
from collections import OrderedDict

mod = Adams.getCurrentModel()

global motionparams
motionparams = OrderedDict()


# ======================================================================================================================
# GetData iterates through each active profile in the ProfileMangaer template.  It is recognized as active if
# Profile name is not blank. For each profile it collects segment points, #steps, fit type and adds the profile name to the
# active profile list (Profile_List). It then calls build segment for each of the profiles.
# ======================================================================================================================

def GET():
    motionparams.clear()
    init_cell = 'B'
    timing_book = xw.Book('ProfileManager.xlsx')
    timing_space = timing_book.sheets('Sheet1')
    Profile_List = []
    for i in range(1, 1000, 10):  # Template has 10 rows between profiles
        if timing_space.range(init_cell + str(i)).value is None:  # End loop if profile name is empty
            continue

        profile_name = timing_space.range(init_cell + str(i)).value
        nsteps = timing_space.range((init_cell + str(i + 1))).value
        septic = timing_space.range((init_cell + str(i + 2))).value
        Profile_List.append(profile_name)  # Add profile name to list of active profiles

        last_col = timing_space.range(init_cell + str(i + 3)).end('right').column  # Find last column in profile set
        profile_data = timing_space.range((i + 3, 2), (i + 3 + 4, last_col))  # Data range of profile points
        BuildSegment(profile_data, profile_name, nsteps, septic)
    MakeSplines(Profile_List)


def BuildSegment(profile_data, profile_name, nsteps, septic):
    # The lines below slice range object data into rows and add each value of the row to a list (e.g. t_values)
    t_values = [cell.value for cell in profile_data[0, :]]
    x_values = [cell.value for cell in profile_data[1, :]]
    v_values = [cell.value for cell in profile_data[2, :]]
    a_values = [cell.value for cell in profile_data[3, :]]
    j_values = [cell.value for cell in profile_data[4, :]]

    Trange_Profile = np.linspace(t_values[0], t_values[-1], int(nsteps))  # create time values for entire profile

    # ===================================================================================================================
    # Step through segments of profile and create Fit Class object for each and add to Odict motionparams where the
    # dict key is the Profile Name + segement number
    # ===================================================================================================================

    for segment in range(0, len(t_values) - 1):
        Profile = profile_name + str(segment)
        t = t_values[segment]
        x = x_values[segment]
        v = v_values[segment]
        a = a_values[segment]
        j = j_values[segment]

        T = t_values[segment + 1]
        X = x_values[segment + 1]
        V = v_values[segment + 1]
        A = a_values[segment + 1]
        J = j_values[segment + 1]

        if str(septic) == 'Y':
            motionparams[Profile] = SepticFit(t, x, v, a, j, T, X, V, A, J, Trange_Profile)
        if str(septic) != 'Y':
            motionparams[Profile] = QuinticFit(t, x, v, a, T, X, V, A,
                                               Trange_Profile)  # create FitClass obj for segment in dict.


def MakeSplines(Profile_List):
    for elem in mod.DataElements.keys():  # interate through existing splines
        for profile in Profile_List:  # check each existing spline against profile list
            countKeys = 0  # count the keys to handle 10+ segments
            keyDigits = 1  # manages 1 & 2 digit keys
            #update displacement
            if str(elem) == str(profile + '1'):  # if spline exists, then existing spline data is updated
                mod.DataElements[elem].active = 'off'
                Taxis = []
                Xaxis = []
                for key in motionparams.keys():
                    countKeys += 1
                    if countKeys > 16:  # allows 10+ segments in profile
                        keyDigits = 2
                    if str(profile) == str(key)[:-keyDigits]:  # This statement will fail if there are more than 10 segments in profile
                        obj = motionparams[key]
                        for t in obj.Trange_Segment:
                            Taxis.append(t)
                        for x in obj.xplot:
                            Xaxis.append(x)
                mod.DataElements[elem].x = Taxis
                mod.DataElements[elem].y = Xaxis
                print('Updated Spline:', profile + '1', 'Type:', obj.fit)
                countKeys = 0  # reset values
                keyDigits = 1
            #update velocity
            if str(elem) == str(profile + '2'):  # if spline exists, then existing spline data is updated
                mod.DataElements[elem].active = 'off'
                Taxis = []
                Vaxis = []
                for key in motionparams.keys():
                    countKeys += 1
                    if countKeys > 16:  # allows 10+ segments in profile
                        keyDigits = 2
                    if str(profile) == str(key)[:-keyDigits]:  # This statement will fail if there are more than 10 segments in profile
                        obj = motionparams[key]
                        for t in obj.Trange_Segment:
                            Taxis.append(t)
                        for v in obj.vplot:
                            Vaxis.append(v)
                mod.DataElements[elem].x = Taxis
                mod.DataElements[elem].y = Vaxis
                print('Updated Spline:', profile + '2', 'Type:', obj.fit)
                countKeys = 0  # reset values
                keyDigits = 1
            #update acceleration
            if str(elem) == str(profile + '3'):  # if spline exists, then existing spline data is updated
                mod.DataElements[elem].active = 'off'
                Taxis = []
                Aaxis = []
                for key in motionparams.keys():
                    countKeys += 1
                    if countKeys > 16:  # allows 10+ segments in profile
                        keyDigits = 2
                    if str(profile) == str(key)[:-keyDigits]:  # This statement will fail if there are more than 10 segments in profile
                        obj = motionparams[key]
                        for t in obj.Trange_Segment:
                            Taxis.append(t)
                        for a in obj.aplot:
                            Aaxis.append(a)
                mod.DataElements[elem].x = Taxis
                mod.DataElements[elem].y = Aaxis
                print('Updated Spline:', profile + '3', 'Type:', obj.fit)
                countKeys = 0  # reset values
                keyDigits = 1
            #update jerk
            if str(elem) == str(profile + '4'):  # if spline exists, then existing spline data is updated
                mod.DataElements[elem].active = 'off'
                Taxis = []
                Jaxis = []
                for key in motionparams.keys():
                    countKeys += 1
                    if countKeys > 16:  # allows 10+ segments in profile
                        keyDigits = 2
                    if str(profile) == str(key)[:-keyDigits]:  # This statement will fail if there are more than 10 segments in profile
                        obj = motionparams[key]
                        for t in obj.Trange_Segment:
                            Taxis.append(t)
                        for j in obj.jplot:
                            Jaxis.append(j)
                mod.DataElements[elem].x = Taxis
                mod.DataElements[elem].y = Jaxis
                print('Updated Spline:', profile + '4', 'Type:', obj.fit)
        mod.DataElements[elem].active = 'on'


    for profile in Profile_List:  # Check each existing spline against profile list
        Taxis = []
        Xaxis = []
        Vaxis = []
        Aaxis = []
        Jaxis = []
        if profile + '1' not in mod.DataElements.keys():  # If splines don't exist create them
            for key in motionparams.keys():
                if profile in key:
                    obj = motionparams[key]
                    for t in obj.Trange_Segment:
                        Taxis.append(t)
                    for x in obj.xplot:
                        Xaxis.append(x)
                    for v in obj.vplot:
                        Vaxis.append(v)
                    for a in obj.aplot:
                        Aaxis.append(a)
                    for j in obj.jplot:
                        Jaxis.append(j)
            # creates 4 splines. displacement -> velocity -> acceleration -> jerk
            mod.DataElements.createSpline(name=profile + '1', x=Taxis, y=Xaxis)
            mod.DataElements.createSpline(name=profile + '2', x=Taxis, y=Vaxis)
            mod.DataElements.createSpline(name=profile + '3', x=Taxis, y=Aaxis)
            mod.DataElements.createSpline(name=profile + '4', x=Taxis, y=Jaxis)
            print('Created Spline:', profile + '1', 'Type:', obj.fit)
            print('Created Spline:', profile + '2', 'Type:', obj.fit)
            print('Created Spline:', profile + '3', 'Type:', obj.fit)
            print('Created Spline:', profile + '4', 'Type:', obj.fit)


class QuinticFit:
    def __init__(self, t, x, v, a, T, X, V, A, Trange_Profile):
        self.t = t
        self.x = x
        self.v = v
        self.a = a

        self.T = T
        self.X = X
        self.V = V
        self.A = A
        self.Trange_Segment = []

        # ===============================================================================================================
        # The for loop below selects the values from Trange_Profile to be used with each segment, this keeps the time
        # step across all segments equal based on the user input nsteps in the profile manager. Wanted to avoid duplicate
        # values (e.g. where time steps land on segment endpoints) which required second if statement. There is probably
        # a more elegent way to do this.
        # ===============================================================================================================

        for i in Trange_Profile:  # creates list of time values for segment from profile list based on n steps
            if i >= t and i < T:
                self.Trange_Segment.append(i)
            if i == Trange_Profile[-1] and T == Trange_Profile[-1]:  # adds last value of Trange_Profile to last segment
                self.Trange_Segment.append(i)

        self.Solve(t, x, v, a, T, X, V, A)

    def Solve(self, t, x, v, a, T, X, V, A):
        Ar = np.array([[self.t ** 5, self.t ** 4, self.t ** 3, self.t ** 2,
                        self.t, 1],
                       [5 * self.t ** 4, 4 * self.t ** 3, 3 * self.t ** 2,
                        2 * self.t, 1, 0],
                       [20 * self.t ** 3, 12 * self.t ** 2, 6 * self.t, 2, 0, 0],
                       [self.T ** 5, self.T ** 4, self.T ** 3, self.T ** 2,
                        self.T, 1],
                       [5 * self.T ** 4, 4 * self.T ** 3, 3 * self.T ** 2,
                        2 * self.T, 1, 0],
                       [20 * self.T ** 3, 12 * self.T ** 2, 6 * self.T, 2, 0, 0]])

        B = np.array([self.x, self.v, self.a, self.X, self.V, self.A])
        self.B = B

        # x=displacement, v=velocity, a=acceleration
        xB = (B[0], 0, 0, B[3], 0, 0)
        vB = (B[0], B[1], 0, B[3], B[4], 0)
        aB = B
        xC = np.linalg.solve(Ar, xB)
        vC = np.linalg.solve(Ar, vB)
        aC = np.linalg.solve(Ar, aB)

        # =======================================================================
        # Make data vectors for x,v,a,j from newly solved equations
        # =======================================================================

        def Dispx(t):
            return (xC[0] * t ** 5 + xC[1] * t ** 4 + xC[2] * t ** 3 +
                    xC[3] * t ** 2 + xC[4] * t + xC[5])

        def Vel(t):
            return (5 * vC[0] * t ** 4 + 4 * vC[1] * t ** 3 + 3 * vC[2] * t ** 2 +
                    2 * vC[3] * t + vC[4])

        def Acc(t):
            return (aC[0] * 20 * t ** 3 + aC[1] * 12 * t ** 2 + aC[2] * 6 * t +
                    aC[3] * 2)

        def j(t):
            return aC[0] * 60 * t ** 2 + aC[1] * 24 * t + aC[2] * 6

        self.xplot = [Dispx(time) for time in self.Trange_Segment]
        self.vplot = [Vel(time) for time in self.Trange_Segment]
        self.aplot = [Acc(time) for time in self.Trange_Segment]
        self.jplot = [j(time) for time in self.Trange_Segment]
        self.fit = 'FifthOrder'
        self.junk = "Junk"
        self.C = xC
        self.Solutions = xC
        self.Coeff = [xC[0], xC[1], xC[2], xC[3], xC[4], xC[5]]
        self.Disp = (xC[0] * t ** 5 + xC[1] * t ** 4 + xC[2] * t ** 3 +
                     xC[3] * t ** 2 + xC[4] * t + xC[5])


class SepticFit:
    # Seventh Order Polynomial Fitting Routine

    def __init__(self, t, x, v, a, j, T, X, V, A, J, Trange_Profile):
        self.t = t
        self.x = x
        self.v = v
        self.a = a
        self.j = j
        self.T = T
        self.X = X
        self.V = V
        self.A = A
        self.J = J
        self.Trange_Segment = []

        for i in Trange_Profile:  # creates list of time values for segment from profile list based on n steps
            if i >= t and i < T:
                self.Trange_Segment.append(i)
            if i == Trange_Profile[-1] and T == Trange_Profile[-1]:  # adds last value of Trange_Profile to last segment
                self.Trange_Segment.append(i)

        self.Solve(t, x, v, a, j, T, X, V, A, J)

    def Solve(self, t, x, v, a, j, T, X, V, A, J):
        Ar = np.array([[self.t ** 7, self.t ** 6, self.t ** 5, self.t ** 4,
                        self.t ** 3, self.t ** 2, self.t, 1],
                       [7 * self.t ** 6, 6 * self.t ** 5, 5 * self.t ** 4,
                        4 * self.t ** 3, 3 * self.t ** 2, 2 * self.t, 1, 0],
                       [42 * self.t ** 5, 30 * self.t ** 4, 20 * self.t ** 3,
                        12 * self.t ** 2, 6 * self.t, 2, 0, 0],
                       [210 * self.t ** 4, 120 * self.t ** 3, 60 * self.t ** 2,
                        24 * self.t, 6, 0, 0, 0],
                       [self.T ** 7, self.T ** 6, self.T ** 5, self.T ** 4,
                        self.T ** 3, self.T ** 2, self.T, 1],
                       [7 * self.T ** 6, 6 * self.T ** 5, 5 * self.T ** 4,
                        4 * self.T ** 3, 3 * self.T ** 2, 2 * self.T, 1, 0],
                       [42 * self.T ** 5, 30 * self.T ** 4, 20 * self.T ** 3,
                        12 * self.T ** 2, 6 * self.T, 2, 0, 0],
                       [210 * self.T ** 4, 120 * self.T ** 3, 60 * self.T ** 2,
                        24 * self.T, 6, 0, 0, 0]])

        B = np.array([self.x, self.v, self.a, self.j, self.X, self.V,
                      self.A, self.J])
        self.B = B

        # x=displacement, v=velocity, a=acceleration, j=jerk
        xB = (B[0], 0, 0, 0, B[4], 0, 0, 0)
        vB = (B[0], B[1], 0, 0, B[4], B[5], 0, 0)
        aB = (B[0], B[1], B[2], 0, B[4], B[5], B[6], 0)
        jB = B
        xC = np.linalg.solve(Ar, xB)
        vC = np.linalg.solve(Ar, vB)
        aC = np.linalg.solve(Ar, aB)
        jC = np.linalg.solve(Ar, jB)

        def Dispx(t):
            return (xC[0] * t ** 7 + xC[1] * t ** 6 + xC[2] * t ** 5 +
                    xC[3] * t ** 4 + xC[4] * t ** 3 +
                    xC[5] * t ** 2 + xC[6] * t + xC[7])

        def Vel(t):
            return (7 * vC[0] * t ** 6 + 6 * vC[1] * t ** 5 + 5 * vC[2] * t ** 4 +
                    4 * vC[3] * t ** 3 + 3 * vC[4] * t ** 2 + 2 * vC[5] * t +
                    vC[6])

        def Acc(t):
            return (42 * aC[0] * t ** 5 + 30 * aC[1] * t ** 4 +
                    20 * aC[2] * t ** 3 + 12 * aC[3] * t ** 2 + 6 * aC[4] * t +
                    2 * aC[5])

        def Jerk(t):
            return (210 * jC[0] * t ** 4 + 120 * jC[1] * t ** 3 +
                    60 * jC[2] * t ** 2 + 24 * jC[3] * t + 6 * jC[4])

        self.xplot = [Dispx(time) for time in self.Trange_Segment]
        self.vplot = [Vel(time) for time in self.Trange_Segment]
        self.aplot = [Acc(time) for time in self.Trange_Segment]
        self.jplot = [Jerk(time) for time in self.Trange_Segment]
        self.fit = 'SeventhOrder'
        self.Solutions = xC