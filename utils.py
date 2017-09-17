class Utils:
    @staticmethod
    def chunk_list(array, num):
        avg = len(array) / float(num)
        out = []
        last = 0.0

        while last < len(array):
            out.append(array[int(last):int(last + avg)])
            last += avg

        for i, inner_list in enumerate(out):
            if len(out[i]) == 0:
                out[i] = out[i + 1]
        return out
