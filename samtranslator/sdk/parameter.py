import boto3
import copy


class SamParameterValues(object):
    """
    Class representing SAM parameter values.
    """

    def __init__(self, parameter_values):
        """
        Initialize the object given the parameter values as a dictionary

        :param dict parameter_values: Parameter value dictionary containing parameter name & value
        """

        self.parameter_values = copy.deepcopy(parameter_values)

    def add_default_parameter_values(self, sam_template):
        """
        Method to read default values for template parameters and merge with user supplied values.

        Example:
        If the template contains the following parameters defined

        Parameters:
            Param1:
                Type: String
                Default: default_value
            Param2:
                Type: String
                Default: default_value

        And, the user explicitly provided the following parameter values:

        {
            Param2: "new value"
        }

        then, this method will grab default value for Param1 and return the following result:

        {
            Param1: "default_value",
            Param2: "new value"
        }


        :param dict sam_template: SAM template
        :param dict parameter_values: Dictionary of parameter values provided by the user
        :return dict: Merged parameter values
        """

        parameter_definition = sam_template.get("Parameters", None)
        if not parameter_definition or not isinstance(parameter_definition, dict):
            return self.parameter_values

        for param_name, value in parameter_definition.items():
            if param_name not in self.parameter_values and isinstance(value, dict) and "Default" in value:
                self.parameter_values[param_name] = value["Default"]

    def add_pseudo_parameter_values(self):
        """
        Add pseudo parameter values
        :return: parameter values that have pseudo parameter in it
        """
        if 'AWS::Region' not in self.parameter_values:
            self.parameter_values['AWS::Region'] = boto3.session.Session().region_name

        if 'AWS::Partition' not in self.parameter_values:
            region = boto3.session.Session().region_name

            # neither boto nor botocore has any way of returning the partition value yet
            if region.startswith('cn-'):
                self.parameter_values['AWS::Partition'] = 'aws-cn'
            elif region.startswith('us-gov-'):
                self.parameter_values['AWS::Partition'] = 'aws-us-gov'
            else:
                self.parameter_values['AWS::Partition'] = 'aws'
