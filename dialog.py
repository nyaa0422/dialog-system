import gensim.downloader as api
from gensim.models.keyedvectors import KeyedVectors

class DialogueStateTracker:
    def __init__(self):
        self.state = {
            "task": None,
            "genre": None,
            "movie": None,
            "restaurant_genre": None,
            "restaurant": None,
            "confirmation": None
        }

    def update_state(self, key, value):
        self.state[key] = value

    def get_state(self):
        return self.state

def movie_options(genre):
    options = {
        "アクション": ["マッドマックス", "ダイハード", "アベンジャーズ"],
        "コメディ": ["ホームアローン", "ミセスダウト", "メンインブラック"],
        "ドラマ": ["ショーシャンクの空に", "フォレストガンプ", "グリーンマイル"]
    }
    return options.get(genre, [])

def restaurant_options(genre):
    options = {
        "イタリアン": ["リストランテA", "トラットリアB", "ピッツェリアC"],
        "中華": ["中華料理店X", "飲茶Y", "四川料理Z"],
        "和食": ["寿司屋1", "天ぷら屋2", "懐石料理3"]
    }
    return options.get(genre, [])

from gensim.models import KeyedVectors

model = KeyedVectors.load_word2vec_format(
    'entity_vector/entity_vector.model.bin',
    binary=True
)

def closest_match(keyword, lst):
    sims = []
    keyword_vector = model[keyword] if keyword in model else None
    if keyword_vector is not None:
        for w in lst:
            try:
                similarity = model.similarity(keyword, w)
            except KeyError:
                similarity = 0 
            sims.append((w, similarity)) 
    print(sims)
    if not sims:
        return None
    return max(sims, key=lambda x: x[1])[0] if sims else None

def get_input():
    return input("テキストを入力してください: ")

def main():
    dst = DialogueStateTracker()
    while True:
        print("映画の予約とレストランの予約、どちらを行いますか？")
        task = get_input()
        task = closest_match(task, ["映画", "レストラン", "キャンセル"])
        print(f"tast:{task}")
        if task:
            if "キャンセル" in task:
                print("キャンセルされました。最初に戻ります。")
                continue
            dst.update_state("task", task)
            if "映画" in task:
                if dst.get_state()["movie"]:
                    print(f"すでに {dst.get_state()['movie']} の予約があります。変更しますか？")
                    change_response = get_input()
                    change_response = closest_match(change_response, ["はい", "ええ", "うん", "いいえ", "キャンセル"])
                    if "キャンセル" in change_response or "いいえ" in change_response:
                        print("キャンセルされました。最初に戻ります。")
                        continue
                    if change_response not in ["はい", "ええ", "うん"]:
                        continue
                print("どのジャンルの映画を見たいですか？")
                print("ジャンルの候補: アクション, コメディ, ドラマ")
                genre = get_input()
                genre = closest_match(genre, ["アクション", "コメディ", "ドラマ"])
                if genre is None or "キャンセル" in genre:
                    print("キャンセルされました。最初に戻ります。")
                    continue
                dst.update_state("genre", genre)
                print(f"{genre} ですね。では､以下の映画からお選び下さい。")
                movie_opts = movie_options(genre)
                if not movie_opts:
                    print("選択したジャンルの映画がありません。最初に戻ります。")
                    continue
                print(f"{genre}の映画の候補: {', '.join(movie_opts)}")
                movie = get_input()
                movie = closest_match(movie, movie_opts)
                if movie is None or "キャンセル" in movie:
                    print("キャンセルされました。最初に戻ります。")
                    continue
                dst.update_state("movie", movie)
                print(f"{movie} ですね｡ 予約しますか？")
                confirm_response = get_input()
                confirm_response = closest_match(confirm_response, ["はい", "ええ", "うん", "いいえ", "キャンセル"])
                if "キャンセル" in confirm_response:
                    print("キャンセルされました。最初に戻ります。")
                    continue
                if confirm_response in ["はい", "ええ", "うん"]:
                    dst.update_state("confirmation", "confirmed")
                    print(f"{movie} の予約が完了しました。")
                else:
                    dst.update_state("confirmation", "cancelled")
                    print("予約をキャンセルしました。")
            elif "レストラン" in task:
                if dst.get_state()["restaurant"]:
                    print(f"すでに {dst.get_state()['restaurant']} の予約があります。変更しますか？")
                    change_response = get_input()
                    change_response = closest_match(change_response, ["はい", "ええ", "うん", "いいえ", "キャンセル"])
                    if "キャンセル" in change_response:
                        print("キャンセルされました。最初に戻ります。")
                        continue
                    if change_response not in ["はい", "ええ", "うん"]:
                        continue
                print("どのジャンルのレストランを予約しますか？")
                print("ジャンルの候補: イタリアン, 中華, 和食")
                genre = get_input()
                genre = closest_match(genre, ["イタリアン", "中華", "和食"])
                if genre is None or "キャンセル" in genre:
                    print("キャンセルされました。最初に戻ります。")
                    continue
                dst.update_state("restaurant_genre", genre)
                print(f"あなたが選んだジャンルは {genre} です。次に、具体的なレストランを選んでください。")
                restaurant_opts = restaurant_options(genre)
                if not restaurant_opts:
                    print("選択したジャンルのレストランがありません。最初に戻ります。")
                    continue
                print(f"{genre}のレストランの候補: {', '.join(restaurant_opts)}")
                restaurant = get_input()
                restaurant = closest_match(restaurant, restaurant_opts)
                if restaurant is None or "キャンセル" in restaurant:
                    print("キャンセルされました。最初に戻ります。")
                    continue
                dst.update_state("restaurant", restaurant)
                print(f"あなたが選んだレストランは {restaurant} です。予約しますか？")
                confirm_response = get_input()
                confirm_response = closest_match(confirm_response, ["はい", "ええ", "うん", "いいえ", "キャンセル"])
                if "キャンセル" in confirm_response:
                    print("キャンセルされました。最初に戻ります。")
                    continue
                if confirm_response in ["はい", "ええ", "うん"]:
                    dst.update_state("confirmation", "confirmed")
                    print(f"{restaurant} の予約が完了しました。")
                else:
                    dst.update_state("confirmation", "cancelled")
                    print("予約をキャンセルしました。")
            else:
                print("選択が認識できませんでした。")
        else:
            print("タスクの選択が認識できませんでした。もう一度お試しください。")
            continue

        print("対話状態:", dst.get_state())

if __name__ == "__main__":
    main()
