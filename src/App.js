import React, { useState, useEffect } from 'react';
import { Calendar, BookOpen, Pen, Archive, ChevronLeft, ChevronRight, Grid } from 'lucide-react';
import { format, parseISO, subDays, addDays, startOfMonth, endOfMonth, eachDayOfInterval } from 'date-fns';
import { Alert, AlertDescription } from '@/components/ui/alert';

const DailyPoetry = () => {
  const [data, setData] = useState(null);
  const [selectedPoem, setSelectedPoem] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isToday, setIsToday] = useState(true);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [showCalendar, setShowCalendar] = useState(false);

  const fetchPoemsByDate = async (date) => {
    setIsLoading(true);
    const dateStr = format(date, 'yyyy-MM-dd');
    const today = format(new Date(), 'yyyy-MM-dd');
    setIsToday(dateStr === today);

    try {
      // Try to fetch from archive first
      let response = await fetch(`/data/archive/${dateStr}.json`);
      
      // If not in archive and it's today, try current poems
      if (!response.ok && dateStr === today) {
        response = await fetch('/data/daily-poems.json');
      }
      
      if (!response.ok) {
        throw new Error('No poems found for this date');
      }
      
      const jsonData = await response.json();
      setData(jsonData);
      setSelectedPoem(jsonData.poems[0]);
      setCurrentDate(parseISO(dateStr));
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPoemsByDate(new Date());
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-900"></div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white dark:from-gray-900 dark:to-gray-800 dark:text-gray-100">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-serif mb-4 text-blue-900 dark:text-blue-100">
            Daily Poetry Collection
          </h1>
          <div className="flex items-center justify-center space-x-4">
            <button 
              onClick={() => fetchPoemsByDate(subDays(currentDate, 1))}
              className="p-2 hover:bg-blue-100 dark:hover:bg-blue-900 rounded-full transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button
              onClick={() => setShowCalendar(!showCalendar)}
              className="flex items-center text-gray-600 dark:text-gray-300 hover:bg-blue-100 dark:hover:bg-blue-900 rounded-lg px-3 py-1"
            >
              <Calendar className="w-5 h-5 mr-2" />
              <span>{format(currentDate, 'MMMM d, yyyy')}</span>
            </button>
            <button 
              onClick={() => fetchPoemsByDate(addDays(currentDate, 1))}
              className="p-2 hover:bg-blue-100 dark:hover:bg-blue-900 rounded-full transition-colors"
              disabled={isToday}
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>

          {showCalendar && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-lg">
                <div className="grid grid-cols-7 gap-2 mb-4">
                  {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                    <div key={day} className="text-center font-medium">{day}</div>
                  ))}
                  {eachDayOfInterval({
                    start: startOfMonth(currentDate),
                    end: endOfMonth(currentDate)
                  }).map(date => (
                    <button
                      key={date.toISOString()}
                      onClick={() => {
                        fetchPoemsByDate(date);
                        setShowCalendar(false);
                      }}
                      className={`p-2 rounded hover:bg-blue-100 dark:hover:bg-blue-900 ${
                        format(date, 'yyyy-MM-dd') === format(currentDate, 'yyyy-MM-dd')
                          ? 'bg-blue-500 text-white'
                          : ''
                      }`}
                    >
                      {format(date, 'd')}
                    </button>
                  ))}
                </div>
                <button
                  onClick={() => setShowCalendar(false)}
                  className="w-full py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  Close
                </button>
              </div>
            </div>
          )}
        </header>

        <div className="grid md:grid-cols-7 gap-6">
          <div className="md:col-span-2 space-y-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
              <h2 className="text-lg font-semibold mb-4 flex items-center">
                <BookOpen className="w-5 h-5 mr-2" />
                Today's Poems
              </h2>
              <div className="space-y-2">
                {data.poems.map((poem, index) => (
                  <button
                    key={index}
                    onClick={() => setSelectedPoem(poem)}
                    className={`w-full text-left px-4 py-2 rounded-md transition-colors ${
                      selectedPoem === poem
                        ? 'bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    <div className="font-medium">{poem.title}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">{poem.author}</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-blue-50 dark:bg-blue-900 rounded-lg shadow-md p-4">
              <h2 className="text-lg font-semibold mb-4 flex items-center">
                <Pen className="w-5 h-5 mr-2" />
                Writing Prompt
              </h2>
              <div className="space-y-2">
                <div className="font-medium">{data.writing_prompt.name}</div>
                <div className="text-sm">
                  <p className="mb-2"><strong>Structure:</strong> {data.writing_prompt.structure}</p>
                  <p className="mb-2"><strong>Rhyme Scheme:</strong> {data.writing_prompt.rhyme_scheme}</p>
                  <p><strong>Prompt:</strong> {data.writing_prompt.prompt}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="md:col-span-5">
            {selectedPoem && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-serif mb-2">{selectedPoem.title}</h2>
                <h3 className="text-gray-600 dark:text-gray-400 mb-6">by {selectedPoem.author}</h3>
                
                <div className="poem-content font-serif mb-8 space-y-1">
                  {selectedPoem.lines.map((line, index) => (
                    <div key={index} className="whitespace-pre-wrap">
                      {line || '\u00A0'}
                    </div>
                  ))}
                </div>

                <div className="analysis space-y-6 prose dark:prose-invert max-w-none">
                  {selectedPoem.analysis.split('\n\n').map((section, index) => {
                    if (section.trim()) {
                      const [title, ...content] = section.split('\n');
                      return (
                        <div key={index}>
                          <h4 className="text-lg font-semibold mb-2">{title}</h4>
                          <div className="text-gray-700 dark:text-gray-300">
                            {content.join('\n')}
                          </div>
                        </div>
                      );
                    }
                    return null;
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DailyPoetry;