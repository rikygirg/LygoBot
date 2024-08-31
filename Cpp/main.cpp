#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <chrono>
#include <numeric>
#include "rapidcsv.h"

using namespace std;

// ------------------------
// FUNCTION DECLARATIONS
// ------------------------

void PrintVector(vector<double>& vec);
double KandleHeight(vector<double>& data, int period = 6);
double EMA(const vector<double>& data, int period, double alpha);
void EMAdf(const vector<double>& data, vector<double>& ema_df, int period, double alpha);
bool CheckBuy(
    const vector<vector<double>>& ema_array,
    const array<double, 2>& boundaries,
    double k_height,
    bool& allowed_to_buy,
    bool& allowed_to_buy_cross,
    bool& is_first_iter,
    bool& is_first_lower
);

// ------------------------
// MAIN FUNCTION
// ------------------------


int main()
{
    double take_profit;
    double stop_loss;
    int NUMBER_FILES_TO_DO;
    cout << "take profit: ";
    cin >> take_profit;
    cout << "stop loss: ";
    cin >> stop_loss;
    cout << "numbers of files: ";
    cin >> NUMBER_FILES_TO_DO;
    
    auto start = chrono::high_resolution_clock::now();
    // Data loading (note that the datasets must be: dataset_num_x.csv where x goes from 1 to N)
    // All csvs must be in the same folder as the exeguible file
    rapidcsv::Document df("dataset_num_1.csv", rapidcsv::LabelParams(0, 0));
    auto end = chrono::high_resolution_clock::now();
    chrono::duration<double> diff = end - start;
    //cout << "loaded csv in " << diff.count() << " s\n";
    long N = df.GetRowCount();
    
    // Initialization
    int n = 202;  // Data points to consider
    int sec_in_min = 60;  // seconds in a minute, for time intervals
    double balance = 1000.0;  // initial balance
    const array<double, 2> boundaries = {2.0, 2.0};  // EMA boundaries for trading decision
    vector<double> data;  // data container

    // Preparing data vector
    for(int i = 0; i < n - 2; i++){
        data.push_back(df.GetCell<double>("close", i * sec_in_min));
    }

    // Initializing EMA vectors
    vector<double> ema100(20, 0.1);
    vector<double> ema200(20, 0.0);
    double alpha100 = 2.0 / (100 + 1.0);
    double alpha200 = 2.0 / (200 + 1.0);
    vector<vector<double>> ema_array;
    double k_height = KandleHeight(data);
    bool allowed_to_buy = true;
    bool allowed_to_buy_cross = false;
    bool is_first_iter = true;
    bool is_first_lower = true;
    
    // Simulation loop
    long tick = n * sec_in_min;
    //cout << "Initial Offset, tick: " << tick << endl;
    bool active_entry = false;
    double price_buy = 0.0;
    double qty_buy = 0.0;
    double tp = 0.0, sl = 0.0;
    double current_price = 0.0;
    
    for (int file = 1; file <= NUMBER_FILES_TO_DO; file++){
        if (file != 1){
            df.Clear();
            df = rapidcsv::Document("dataset_num_" + to_string(file) + ".csv", rapidcsv::LabelParams(0, 0));
            tick = n * sec_in_min;
            N = df.GetRowCount();
        }
        cout << "Doing file " << file << endl;
        while (tick < N - n * sec_in_min) {
            if (tick % sec_in_min == 0) {
                data.erase(data.begin());
                data.push_back(df.GetCell<double>("close", tick));
                k_height = KandleHeight(data);
                EMAdf(data, ema100, 100, alpha100);
                EMAdf(data, ema200, 200, alpha200);
                ema_array = {
                    {ema100.back(), ema200.back()},
                    {ema100.front(), ema200.front()}
                };
            } else {
                data.back() = df.GetCell<double>("close", tick);
                k_height = KandleHeight(data);
            }
            // DEBUGGING:
            //ofstream file(output_file_path, ios::app);
            //file << df.GetCell<string>("date", tick) << ", ("
            //             << ema_array[0][0] << ", " << ema_array[0][1] << ", "
            //             << ema_array[1][0] << ", " << ema_array[1][1] << ")\n";
            // Trading logic
            if (active_entry) {
                current_price = data.back();
                if (current_price > tp) {
                    balance += current_price * qty_buy;
                    //cout << df.GetCell<string>("date", tick) << " Sold " << qty_buy << " BTC " << "at: ";
                    //cout << data.back() << " WIN" << endl;
                    //cout << "Balance: " << balance << "\n" << endl;
                    active_entry = false;
                } else if (current_price < sl) {
                    balance += current_price * qty_buy;
                    //cout << df.GetCell<string>("date", tick) << " Sold " << qty_buy << " BTC " << "at: ";
                    //cout << data.back() << " LOSS" << endl;
                    //cout << "Balance: " << balance << "\n" << endl;
                    active_entry = false;
                }
            } else {
                if (CheckBuy(ema_array, boundaries, k_height, allowed_to_buy, allowed_to_buy_cross, is_first_iter, is_first_lower)) {
                    price_buy = data.back();
                    qty_buy = int(balance / price_buy * 1000) / 1000.0;
                    balance -= price_buy * qty_buy;
                    tp = price_buy + k_height * take_profit;
                    sl = price_buy - k_height * abs(stop_loss);
                    active_entry = true;
                    //printf("%f\n", qty_buy);
                    //cout << tick << endl;
                    //cout << df.GetCell<string>("date", tick) << " Bought " << qty_buy << " BTC " << "at: ";
                    //cout << price_buy << " TP: " << tp << " SL: " << sl << " Kh: (" << k_height << ")" << endl;
                }
            }
            tick++;
        }
        
        
    }

    // Output final balance and total execution time
    cout << "TP: " << take_profit << " SL: " << stop_loss << endl;
    cout << "Final balance: " << balance << endl;
    end = chrono::high_resolution_clock::now();
    diff = end - start;
    cout << "Total execution time: " << diff.count() << " s\n";
    return 0;
}

// ------------------------
// FUNCTION DEFINITIONS
// ------------------------

void PrintVector(vector<double>& vec){
    for (double elem : vec) {
        cout << elem << endl;
    }
    cout << endl;
}

double KandleHeight(vector<double>& data, int period) {
    double kandle_height = 0.0;
    for (long i = data.size() - period - 2; i <= data.size() - 3; ++i) {
        kandle_height += abs(data[i + 1] - data[i]);
    }
    return kandle_height / period;
}

double EMA(const std::vector<double>& data, int period, double alpha) {
    double ema = *(data.end()-period-1);
        for (auto it = data.end() - period; it != data.end()-1; it++) {
            ema = alpha * (*it) + (1 - alpha) * ema;
        }
        return ema;
    }

void EMAdf(const vector<double>& data, vector<double>& ema_df, int period, double alpha){
    //double ema_value = EMA(data, period, alpha);
    double ema_value = data.back() * alpha + ema_df.back() * (1 - alpha);
    ema_df.push_back(ema_value);
    ema_df.erase(ema_df.begin());
}

bool CheckBuy(
    const vector<vector<double>>& ema_array,
    const array<double, 2>& boundaries,
    double k_height,
    bool& allowed_to_buy,
    bool& allowed_to_buy_cross,
    bool& is_first_iter,
    bool& is_first_lower
) {
    int z = 0;
    // Check for buying conditions based on boundaries and K_HEIGHT
    if ((ema_array[z][0] - ema_array[z][1] > boundaries[0] * k_height) ||
        (ema_array[z][1] - ema_array[z][0] > boundaries[1] * k_height)) {
        allowed_to_buy = true;
    }

    // Check the next set of EMAs if they exist
    if (z + 1 < ema_array.size()) {
        if (ema_array[z + 1][1] < ema_array[z + 1][0]) {
            allowed_to_buy_cross = false;
        } else {
            allowed_to_buy_cross = true;
        }
    }

    // Check if it's the first iteration
    if (is_first_iter) {
        is_first_lower = ema_array[z][0] < ema_array[z][1];
        is_first_iter = false;
    }

    // Logic to determine the buy signal
    if ((is_first_lower && ema_array[z][0] >= ema_array[z][1]) ||
        (!is_first_lower && ema_array[z][0] < ema_array[z][1])) {
        if (is_first_lower && ema_array[z][0] >= ema_array[z][1]) {
            is_first_lower = false;
        } else {
            is_first_lower = true;
        }

        bool result = allowed_to_buy && allowed_to_buy_cross;
        allowed_to_buy = false;
        if (result)
            //cout << ema_array[0][0] << " " << ema_array[0][1] << " " << ema_array[1][0] << " " << ema_array[1][1] << endl;
        return result;
    }

    return false;
}
