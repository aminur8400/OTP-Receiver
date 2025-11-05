<?php
namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Number;
use App\Models\NumberAssignment;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class NumberController extends Controller
{
    public function countries(){
        return response()->json(Number::select('country')->distinct()->pluck('country'));
    }

    public function numbersByCountry($country){
        // return numbers (pagination optional)
        $numbers = Number::where('country', $country)->paginate(50);
        return response()->json($numbers);
    }

    public function claimRandom(Request $r){
        $user = $r->user();

        // server cooldown enforcement
        $last = NumberAssignment::where('user_id',$user->id)->orderBy('created_at','desc')->first();
        if($last && $last->created_at->diffInSeconds(now()) < 10){
            return response()->json(['error'=>'Cooldown active. Wait a few seconds.'],429);
        }

        $country = $r->input('country');

        $selected = DB::transaction(function() use($country, $user){
            $qry = Number::where('is_active',1);
            if($country) $qry->where('country',$country);

            $sub = DB::table('number_assignments')
                ->select('number_id')
                ->where('active',1)
                ->where('expire_at','>', now());

            $num = $qry->whereNotIn('id',$sub)->inRandomOrder()->lockForUpdate()->first();
            if(!$num) return null;

            // deactivate old assignments for that number
            NumberAssignment::where('number_id',$num->id)->update(['active'=>false]);

            $assign = NumberAssignment::create([
                'user_id' => $user->id,
                'number_id' => $num->id,
                'assigned_at' => now(),
                'expire_at' => now()->addMinutes(5),
                'active' => true
            ]);

            return ['number'=>$num,'assignment'=>$assign];
        });

        if(!$selected) return response()->json(['error'=>'No available number'],404);

        return response()->json([
            'number' => $selected['number']->number,
            'assignment_id' => $selected['assignment']->id,
            'expire_at' => $selected['assignment']->expire_at
        ]);
    }

    public function userAssignments(Request $r){
        $assignments = $r->user()->assignments()->where('expire_at','>',now())->where('active',true)->get();
        return response()->json($assignments);
    }
}
