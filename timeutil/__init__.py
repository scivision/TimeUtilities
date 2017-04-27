from datetime import date, datetime
from matplotlib.dates import date2num, num2date
from math import floor
from numpy import arctan2, arcsin, sin, cos, pi


class TimeUtilities(object):

    """ Several mehods to deal with time-series lists and plots
    """

    def __init__(self):
        pass


    def ToTime(self, year, month, dom, hh=0, mm=0, ss=0, micsec=0):

        """ Return floating-point number representing the number of days
            since 0001-01-01 00:00:00 UTC, plus one.
        """
        d = datetime(year, month, dom, hh, mm, ss, micsec) - datetime(1,1,1)
        dd = d.days
        if d.seconds > 0:
            dd += d.seconds/86400.

        return dd + 1.  # +1 by convention


    def CalcDOY(self, year, month, dom):

        """ Return the day of year
        """

        return int(self.ToTime(year, month, dom) - self.ToTime(year, 1, 1) + 1.)


    def IsLeapYear(self, year):

        """ Check if a year is leap
        """
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)



    def CalcMDOM(self, doy, year):

        """
        Given the "day of the year" (doy) and "year" (year) numbers, provides
        values of "month" (curr_month) and "day of the month" (curr_dom)

        Syntaxis:
            month, dom = CalcMDOM( doy, year )

        """

        fmdoy = [self.CalcDOY(year, i + 1, 1) for i in range(12)]
        cMonth = len(list(filter(lambda x : x <= doy, fmdoy)))
        cDOM = doy - fmdoy[cMonth - 1] + 1

        return cMonth, cDOM


    def ToHMS(self, hr):

        """ Convert hr floating-value into [hour, minute, second]
        """

        hh_f = hr
        hh = int(floor(hh_f))

        mm_f = 60. * (hr - float(hh))
        mm = int(floor(mm_f))

        ss_f = 60. * (mm_f - float(mm))
        ss = int(floor(ss_f))

        return hh, mm, ss

    #
    # End of 'ToHMS'
    #####


    def ToMoonTime( self, year, month, dom, hour=0, minute=0, second=0 ):

        """
        Convert Earth's time to lunar clock

        Details on conversion at:
        http://lunarclock.org/lunar-clock.php

        Results can be verified with "Convert a date to Lunar standard"
        available at:
        http://lunarclock.org/convert-to-lunar-standard-time.php

        """

        # Time to be converted ...
        ts = datetime(year,month,dom,hour,minute,second)

        # Neil Armstrong set foot on the Moon on July 21st, 1969 at 02:56:15 UT so
        # this is the point in time for the calendar to start
        #t0 = time_util.totime( 1969, 7, 21, 2, 56, 15, 0 )[ 0 ]
        t0 = datetime( 1969, 7, 21, 2, 56, 15, 0 )

        tlp = ( ts - t0 ).total_seconds()

        # a lunar second in terrestrial seconds
        lsec2tsec = 0.9843529666671

        # lunar cycle to terrestrial seconds
        lcy2tsec = 86400 * lsec2tsec

        # Time lapsed in number of lunar cycles
        tlp /= lcy2tsec

        # As 't0' represents 01-01-01 'nabla' 00:00:00, I add 1 lunar year,
        # 1 lunar day, and 1 lunar cycle, in lunar cycle units
        tlp += 12 * 30 + 30 + 1

        # from lunar cycles to lunar hour
        dummy = tlp % 1 * 24
        lhour = int(dummy)

        # from lunar hour to lunar minute
        dummy = dummy % 1 * 60
        lminute = int(dummy)

        # from lunar minutes to lunar seconds
        dummy = dummy % 1 * 60
        lsecond = int(dummy)

        # lunar year
        dummy = tlp / (12. * 30.)
        lyear = int(dummy)

        # lunar day
        dummy = dummy % 1 * 12
        lday = int(dummy)

        # lunar cycle
        dummy = dummy % 1 * 30
        lcycle = int(dummy)

        return lyear, lday, lcycle, lhour, lminute, lsecond


    def UT2LT(self, ut, glon, iyyy, ddd):

        """ Convert UTC to Local Time
        """

        xlon = ( glon - 360. if glon > 180. else glon )
        slt = ut + xlon / 15.
        if (slt >= 0.) & (slt <= 24.): return slt

        if slt > 24.:
            slt -= 24.
            ddd += 1.
            dddend = 365.
            if (iyyy / 4. * 4. == iyyy): dddend = 366.
            if (ddd > dddend):
                iyyy += 1.
                ddd = 1.
            return slt

        slt += 24.
        ddd -= 1.
        if (ddd < 1.):
            iyyy -= 1.
            ddd = 365.
            # leap year if evenly divisible by 4 and not by 100, except if evenly
            # divisible by 400. Thus 2000 will be a leap year.
            if (iyyy / 4. * 4. == iyyy): ddd = 366.

        return slt


    def TimeLabel(self, dt, strutc='UT'):
        """ Generate x-axis label needed in time-series plots
        """

        d = num2date(dt)

        if int(dt[1] - dt[0]) >= 1:
            tlabel = "%s-%s (%s)" % (d[0].strftime('%m/%d'),
                                     d[1].strftime('%d/%Y'), strutc)
            tfname = '%s-%s' % (d[0].strftime('%Y%m%d'),
                                d[1].strftime('%Y%m%d'))
        else:
            tlabel = "%s (%s)" % (d[0].strftime('%m/%d/%Y'), strutc)
            tfname = '%s'      % d[0].strftime('%Y%m%d')

        return tlabel, tfname


    def S2DN(self, input):

        """ Convert # of seconds from 1/1/1970 to number of days from 1/1/1
        """

        return(input / (24 * 3600.) + date2num(date(1970, 1, 1)))


    def JD2GD(self, input):

        """ Convert Julian to Greogorian time
        """

        inseconds = 86400. * (input - self.GD2JD(1970, 1, 1, 0, 0, 0))

        return self.S2DN(inseconds)


    def GD2JD(self, year, month, dom, hour=12, minute=0, second=0):

        """ Convert Gregorian time to Julian date
        """

        ut = hour + minute / 60. + second / 3600.
        total_seconds = hour * 3600. + minute * 60. + second
        fracday = total_seconds / 86400.
        sig = ( 1 if (100 * year + month -190002.5) > 0 else -1 )
        jd = 367. * year - int(7 * (year + int((month + 9) / 12)) / 4) + \
            int(275 * month / 9) + dom + 1721013.5 + ut / 24 - 0.5 * sig + 0.5

        return jd


    def SubSol(self, datetime):

        """
            Subsolar geocentric latitude and longitude.
        """

        # convert to year, day of year and seconds since midnight
        year = datetime.year
        doy = datetime.timetuple().tm_yday
        ut = datetime.hour*3600 + datetime.minute*60 + datetime.second

        if not 1601 <= year <= 2100:
            raise ValueError('Year must be in [1601, 2100]')

        yr = year - 2000

        nleap = floor((year-1601)/4)
        nleap = nleap - 99
        if year <= 1900:
            ncent = floor((year-1601)/100)
            ncent = 3 - ncent
            nleap = nleap + ncent

        l0 = -79.549 + (-0.238699*(yr-4*nleap) + 3.08514e-2*nleap)

        g0 = -2.472 + (-0.2558905*(yr-4*nleap) - 3.79617e-2*nleap)

        # Days (including fraction) since 12 UT on January 1 of IYR:
        df = (ut/86400 - 1.5) + doy

        # Addition to Mean longitude of Sun since January 1 of IYR:
        lf = 0.9856474*df

        # Addition to Mean anomaly since January 1 of IYR:
        gf = 0.9856003*df

        # Mean longitude of Sun:
        l = l0 + lf

        # Mean anomaly:
        g = g0 + gf
        grad = g*pi/180

        # Ecliptic longitude:
        lmbda = l + 1.915*sin(grad) + 0.020*sin(2*grad)
        lmrad = lmbda*pi/180
        sinlm = sin(lmrad)

        # Days (including fraction) since 12 UT on January 1 of 2000:
        n = df + 365*yr + nleap

        # Obliquity of ecliptic:
        epsilon = 23.439 - 4e-7*n
        epsrad = epsilon*pi/180

        # Right ascension:
        alpha = arctan2(cos(epsrad)*sinlm, cos(lmrad)) * 180/pi

        # Declination:
        delta = arcsin(sin(epsrad)*sinlm) * 180/pi

        # Subsolar latitude:
        sslat = delta

        # Equation of time (degrees):
        etdeg = l - alpha
        nrot = round(etdeg/360)
        etdeg = etdeg - 360*nrot

        # Apparent time (degrees):
        aptime = ut/240 + etdeg    # Earth rotates one degree every 240 s.

        # Subsolar longitude:
        sslon = 180 - aptime
        nrot = round(sslon/360)
        sslon = sslon - 360*nrot

        return sslat, sslon


#
# End of "TimeUtilities"
#####




if __name__ == '__main__':

    pass
