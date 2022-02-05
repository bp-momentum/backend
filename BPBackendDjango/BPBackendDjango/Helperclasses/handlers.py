class ErrorHandler():

    @staticmethod
    def check_arguments(expected_header, header, expected_data, data):
        missing_header = []
        missing_data = []
        missing = False

        for h in expected_header:
            if header.get(h) == None:
                missing_header.append(h)
                missing = True

        for d in expected_data:
            if data.get(d) == None:
                missing_data.append(d)
                missing = True

        return {
            'valid': not missing,
            'missing': {
                'header': missing_header,
                'data': missing_data
            }
        }