import json

class ParamsManager:
    def __init__(self, params_file='params.json'):
        self.params = self.load_params(params_file)

    def load_params(self, params_file=None):
        try:
            defaults=json.load(open("params_default.json"))
        except Exception as e:
            print("params_default.json file is missing")
            raise e 
        if params_file == None:
            return defaults
        try:
            params=json.load(open(params_file))
        except Exception as e:
            print("Failed to load parameter file {:s}".format(params_file))
            raise e
        #--------------------------------------------------------------------------
        # print(params)
        # go through all parameters given in the params file and
        # overwrite the defaults with any that are given
        #--------------------------------------------------------------------------
        for p in defaults:
            if p in params:
                defaults[p]=params[p]
            else:
                print("Parameter {:s} not specified in {:s} using default of ".format(p,params_file),defaults[p])
        for p in params:
            if p not in defaults:
                defaults[p] = params[p]
        #--------------------------------------------------------------------------        
        # make sure freqency is within hackrf range
        #--------------------------------------------------------------------------
        if defaults["frequency"] < 30e6 or defaults["frequency"] > 6e9:
            #raise Excpetion("Frequency {:e} out of range".format(defaults["frequency"]))
            raise Exception("Frequency {:e} out of range".format(defaults["frequency"]))
        self.params = defaults
        return defaults

    @staticmethod
    def save_params(params, params_file, overwrite=True):
        """
        Save the params to a params file.
        Will overwrite by default.

        Args:
            params (dict): Dictionary of parameters to save.
            params_file (str): Path to the parameters file.
            overwrite (bool, optional): Whether to overwrite existing file. Defaults to True.
        """
        if not overwrite:
            try:
                f = open(params_file, 'r')
                f.close()
                raise Exception("File {:s} exists and overwrite is set to False".format(params_file))
            except FileNotFoundError:
                pass
        with open(params_file, 'w') as f:
            json.dump(params, f, indent=4)
