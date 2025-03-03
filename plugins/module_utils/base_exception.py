from ansible.module_utils.common.text.converters import to_native


class BaseAnsibleError(Exception):
    """
    This is the base class for all errors raised from Ansible code,
    and can be instantiated with two optional parameters beyond the
    error message to control whether detailed information is displayed
    when the error occurred while parsing a data file of some kind.

    Usage:

        raise AnsibleError('some message here', obj=obj, show_content=True)

    Where "obj" is some subclass of ansible.parsing.yaml.objects.AnsibleBaseYAMLObject,
    which should be returned by the DataLoader() class.
    """

    def __init__(
        self,
        message="",
        obj=None,
        show_content=True,
        suppress_extended_error=False,
        orig_exc=None,
    ):
        super(BaseAnsibleError, self).__init__(message)

        self._show_content = show_content
        self._suppress_extended_error = suppress_extended_error
        self._message = to_native(message)
        self.obj = obj
        self.orig_exc = orig_exc

    @property
    def message(self):
        message = [self._message]

        # Add from previous exceptions
        if self.orig_exc:
            message.append(". %s" % to_native(self.orig_exc))

        return "".join(message)

    @message.setter
    def message(self, val):
        self._message = val

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message

    def _get_error_lines_from_file(self, file_name, line_number):
        """
        Returns the line in the file which corresponds to the reported error
        location, as well as the line preceding it (if the error did not
        occur on the first line), to provide context to the error.
        """

        target_line = ""
        prev_line = ""

        with open(file_name, "r") as f:
            lines = f.readlines()

            # In case of a YAML loading error, PyYAML will report the very last line
            # as the location of the error. Avoid an index error here in order to
            # return a helpful message.
            file_length = len(lines)
            if line_number >= file_length:
                line_number = file_length - 1

            # If target_line contains only whitespace, move backwards until
            # actual code is found. If there are several empty lines after target_line,
            # the error lines would just be blank, which is not very helpful.
            target_line = lines[line_number]
            while not target_line.strip():
                line_number -= 1
                target_line = lines[line_number]

            if line_number > 0:
                prev_line = lines[line_number - 1]

        return (target_line, prev_line)
