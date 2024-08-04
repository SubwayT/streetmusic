from flask import Flask, request, render_template, redirect, url_for
import psycopg2

# データベースの設定は各自のものに修正すること
connection = psycopg2.connect("host=localhost dbname=g2450003 user=g2450003 password=xscaHWar")
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            place_id = request.form['place']
            nickname = request.form['nickname']
            attendance = request.form['attendance']
            setlist = [
                request.form['setlist1'],
                request.form['setlist2'],
                request.form['setlist3'],
                request.form['setlist4'],
                request.form['setlist5']
            ]
            setlist = ', '.join(filter(None, setlist))  # 空の入力を除いて結合
            donation = request.form['donation']
            event_date = request.form['event_date']

            cursor = connection.cursor()
            cursor.execute("INSERT INTO entries (place_id, nickname, attendance, setlist, donation, event_date) VALUES (%s, %s, %s, %s, %s, %s)",
                           (place_id, nickname, attendance, setlist, donation, event_date))
            connection.commit()
            cursor.close()
            return redirect(url_for('index'))  # POST後にリダイレクトして二重送信を防ぐ
        except Exception as e:
            print(f'Error adding entry: {str(e)}')

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, name FROM streetmusic")
        places = cursor.fetchall()

        cursor.execute("""
            SELECT 
                streetmusic.name, 
                streetmusic.lat, 
                streetmusic.lon, 
                string_agg(entries.nickname || ' (動員数: ' || entries.attendance || ', セトリ: ' || entries.setlist || ', 投げ銭: ' || entries.donation || ', 日付: ' || entries.event_date || ')', '<br>') as artist_info 
            FROM entries 
            JOIN streetmusic ON entries.place_id = streetmusic.id 
            GROUP BY streetmusic.name, streetmusic.lat, streetmusic.lon
        """)
        entries = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print(f'Error fetching data: {str(e)}')
        places = []
        entries = []

    return render_template('index.html', places=places, entries=entries)

@app.route('/delete/<int:entry_id>')
def delete_entry(entry_id):
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM entries WHERE id = %s", (entry_id,))
        connection.commit()
        cursor.close()
        print(f'Entry {entry_id} deleted.')
    except Exception as e:
        print(f'Error deleting entry: {str(e)}')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
