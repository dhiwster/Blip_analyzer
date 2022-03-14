import numpy as np
from BaseDriver import LabberDriver


class Driver(LabberDriver):
    """Detect blips in single shot traces"""

    def performOpen(self, options={}):
        """Perform the operation of opening the instrument connection."""
        self.blip = Blip()
        self.blip.sampling_rate = self.getValue("Sampling Rate")

    def performSetValue(self, quant, value, sweepRate=0.0, options={}):
        """Perform the Set Value instrument operation."""
        if "Search Window 1" in quant.name:
            window = self.blip.searchwindow
            window[0] =value
            self.blip.searchwindow = window
        elif "Search Window 2" in quant.name:
            window = self.blip.searchwindow
            window[1] =value
            self.blip.searchwindow = window
        elif "Trace" in quant.name:
            if value is not None:
               self.blip.trace = value["y"]
        else:
            name = quant.set_cmd
            type(self.blip).__dict__[name].__set__(self.blip, value)

    def performGetValue(self, quant, options={}):
        """Perform the Get Value instrument operation."""
        if "Search Window 1" in quant.name:
            return self.blip.searchwindow[0]
        elif "Search Window 2" in quant.name:
            return self.blip.searchwindow[1]
        else:
            self.log("The trace: !",level=30)
            self.log(self.blip._trace,level=30)
            name = quant.get_cmd
            return getattr(self.blip,name)


    def result_to_quant(self, quant, Blip):
        """Gets the corresponding result data from the scope module."""
        if Blip.trace.size > 0:
            y = Blip.trace
            return quant.getTraceDict(y)
        else:
            return np.array([])

class Blip:
    def __init__(self):
        self.sampling_rate = 1.8e9
        self.searchwindow = np.array([np.nan,np.nan])
        self.refwindow = np.array([np.nan,np.nan])
        self.threshold = np.nan
        self.reflevel = np.nan
        self.trace = np.array([])
        self.segmentlength = 1
        self.probability = np.nan
        self.I_avg = np.nan
        self._t=np.array([]) #Not sure whether this should be a protected property
        self._count = np.nan
        self._searchindex = np.array([np.nan,np.nan])
        self._trace_reshaped = np.array([])
        self._mean_timetrace = np.array([])

    @property
    def sampling_rate(self):
        return self._sampling_rate

    @sampling_rate.setter
    def sampling_rate(self,value):
        self._sampling_rate = value
        # Will be nice to set the time axis array as well

    @property
    def searchwindow(self):
        return self._searchwindow

    @searchwindow.setter
    def searchwindow(self, value):
        self._searchwindow = value
        self._searchindex = self._searchwindow*self.sampling_rate
        self._searchindex = self._searchindex.astype(int)

    @property
    def refwindow(self):
        return self.refwindow

    @refwindow.setter
    def refwindow(self, value):
        self._refwindow = value

    @property
    def _refindex(self):
        self._refindex = self.refwindow*self.sampling_rate
        return self._refindex

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        self._threshold = value

    @property
    def trace(self):
        return self._trace

    @trace.setter
    def trace(self, value):
        if isinstance(value, np.ndarray) == 0:
            value = np.array(value)

        self._trace = value

    @property
    def segmentlength(self):
        return self._segmentlength

    @segmentlength.setter
    def segmentlength(self, value):
        self._segmentlength = int(value)
        if self.trace.size > 0:
            self.update()

    @property
    def reflevel(self):
        # Reference level for every trace to discard jumps etc
        return self._reflevel

    @reflevel.setter
    def reflevel(self, value):
        self._reflevel = value

    @property
    def probability(self):
        self.update()
        return self._probability

    @probability.setter
    def probability(self, value):
        self._probability = value

    @property
    def I_avg(self):
        self.update()
        return self._I_avg

    @I_avg.setter
    def I_avg(self, value):
        self._I_avg = value

    @property
    def mean_timetrace(self):
        self.update()
        return self._mean_timetrace

    def update(self):
        trace = self._trace

        if trace.size>0:
            L = self._segmentlength
            number_of_records=int(np.ceil(trace.size/L))
            trace = np.append(
                trace, np.nan*np.zeros(number_of_records*L-trace.size))
            trace = trace.reshape(number_of_records, L)

            if np.isnan(self.reflevel) == 0:
                trace = trace - self._reflevel
                # # Search for blip
            if np.any(np.isnan(self._searchwindow)) == 0:
                searchind = self._searchindex
                self._count = np.sum(
                    np.any(trace[:, searchind[0]:searchind[1]] > self._threshold, axis=1))
                self._probability = self._count/trace.shape[0]
                self._I_avg = np.nanmean(trace[:, searchind[0]:searchind[1]])


            self._mean_timetrace = np.nanmean(trace,axis=0)
            self._trace_reshaped = trace
            self._t = np.arange(L)/self.sampling_rate

if __name__ == "__main__":
    pass
