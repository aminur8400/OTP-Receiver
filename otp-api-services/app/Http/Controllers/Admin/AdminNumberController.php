<?php
namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\Number;
use App\Models\Withdrawal;
use App\Models\User;
use Maatwebsite\Excel\Facades\Excel;
use App\Imports\NumbersImport;

class AdminNumberController extends Controller
{
    public function upload(Request $r){
        $r->validate(['file'=>'required|mimes:xlsx,xls,csv']);
        Number::truncate();
        Excel::import(new NumbersImport, $r->file('file'));
        return response()->json(['ok'=>true]);
    }

    public function usersList(){
        $users = User::select('id','name','email','points')->orderBy('points','desc')->get();
        return response()->json($users);
    }

    public function withdrawRequests(){
        return response()->json(Withdrawal::with('user')->orderBy('created_at','desc')->get());
    }

    public function approveWithdrawal($id){
        $w = Withdrawal::findOrFail($id);
        if($w->status !== 'pending') return response()->json(['error'=>'Already processed'],422);

        \DB::transaction(function() use($w){
            $w->status = 'approved';
            $w->save();
            $u = $w->user;
            $u->points = max(0, $u->points - $w->points);
            $u->save();
            // log in user_points
            \App\Models\UserPoint::create(['user_id'=>$u->id,'points'=> -$w->points,'reason'=>'Withdrawal']);
            // optionally generate invoice row here
        });

        return response()->json(['ok'=>true]);
    }

    public function rejectWithdrawal($id){
        $w = Withdrawal::findOrFail($id);
        if($w->status !== 'pending') return response()->json(['error'=>'Already processed'],422);
        $w->status = 'rejected';
        $w->save();
        return response()->json(['ok'=>true]);
    }
}
