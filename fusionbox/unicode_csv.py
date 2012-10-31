"""
Unicode Readers and Writers for use with the stdlib's csv module.

See <http://docs.python.org/library/csv.html> for details.
"""
import csv
import codecs
import cStringIO


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)
        self.line_num = 0

    def next(self):
        row = self.reader.next()
        self.line_num = self.reader.line_num
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class UnicodeDictWriter(csv.DictWriter):
    def __init__(self, f, fieldnames, restkey="", extrasaction="raise",
                 dialect="excel", encoding="utf-8", *args, **kwargs):
        csv.DictWriter.__init__(self, f, fieldnames, restkey, extrasaction,
                                dialect, *args, **kwargs)
        self.writer = UnicodeWriter(f, dialect, encoding=encoding, *args, **kwargs)


class UnicodeDictReader(csv.DictReader):
    def __init__(self, f, fieldnames=None, restkey=None, restval=None,
                 dialect="excel", encoding="utf-8", *args, **kwargs):
        csv.DictReader.__init__(self, f, fieldnames, restkey, restval,
                                dialect, *args, **kwargs)
        self.reader = UnicodeReader(f, dialect, encoding=encoding, *args, **kwargs)
