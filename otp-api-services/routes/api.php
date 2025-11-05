<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ProfileController;
use App\Http\Controllers\NumberController;
use App\Http\Controllers\Admin\AdminNumberController;
use App\Http\Controllers\WithdrawalController;
use App\Http\Controllers\UserDataController;

Route::middleware('auth:sanctum')->group(function () {
    // Profile
    Route::get('/profile', [ProfileController::class, 'show']);
    Route::post('/profile', [ProfileController::class, 'updateProfile']);
    Route::post('/change-password', [ProfileController::class, 'changePassword']);
    Route::post('/payment-method', [ProfileController::class, 'addPaymentMethod']);
    Route::get('/payment-methods', [ProfileController::class, 'listPaymentMethods']);

    // Working page / numbers
    Route::get('/numbers/countries', [NumberController::class, 'countries']);
    Route::get('/numbers/{country}', [NumberController::class, 'numbersByCountry']);
    Route::post('/numbers/claim', [NumberController::class, 'claimRandom']); // POST {country?}
    Route::get('/user/assignments', [NumberController::class, 'userAssignments']); // user's active assignments

    // User SMS & points
    Route::get('/user/sms', [UserDataController::class, 'userSms']); // list sms belonging to user
    Route::get('/user/points', [UserDataController::class, 'points']);

    // Withdraw
    Route::post('/withdraw', [WithdrawalController::class, 'requestWithdrawal']);
});

// Admin routes
Route::middleware(['auth:sanctum','admin'])->group(function(){
    Route::post('/admin/numbers/upload', [AdminNumberController::class,'upload']);
    Route::get('/admin/users', [AdminNumberController::class,'usersList']); // overview
    Route::get('/admin/withdrawals', [AdminNumberController::class,'withdrawRequests']);
    Route::post('/admin/withdrawals/{id}/approve', [AdminNumberController::class,'approveWithdrawal']);
    Route::post('/admin/withdrawals/{id}/reject', [AdminNumberController::class,'rejectWithdrawal']);
});
