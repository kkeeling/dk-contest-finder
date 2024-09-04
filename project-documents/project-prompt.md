# Project: DraftKings Contest Finder Agent

## Project Description

This project creates an autonomous agent that scrapes various "lobbies" on DraftKings, processes the experience level of all of these entrants, and then sends a message to a Slack Channel when it finds a contest where the experience level meets a certain threshold.

### Agent Workflow

1. Call getContests endpoint: <https://www.draftkings.com/lobby/getcontests?sport={sport}>, where sport is a valid sport abbreviation (ex. NFL, NHL, TEN, etc). The list of available sports is attached.
2. For each contest, add the contest to the dk_contests table if it is not already present and meets any of the following criteria:
    - Contains fewer than 10 entrants
    - Title includes the word "Double Up"
3. For each contest in the found in step 1 and meeting the criteria in step 2, navigate to <https://www.draftkings.com/contest/detailspop?contestId={contestId}> where contestId is collected in the previous steps through the "id" property of each contest. This step will require authentication with DraftKings. Also, this step should include newly found contests AND contests that have not yet been marked as ready_to_enter. However, it should not include contests that have not been added to the dk_contests table.
4. Extract the entrants in the contest, which can be found in the "Entrants" section of the page. Discard any non Double Up contests containing any entrant where the user name is in the blacklisted list. The initial blacklist is: theleafnode, clivebixby, lakergreat.
5. Extract the experience level of each entrant in the contest, and assign each entrant a value of 0 to beginners, 1 to low, 2 to medium, and 3 to highest experience levels.
6. Count the number of entrants at the highest experience level, and divide by the number of entrants. If this value is less than 0.3 update the contest in the dk_contests table by marking it as "ready_to_enter".
7. Send a message to the Slack Channel containing a link to the contest using the following url template: <https://www.draftkings.com/draft/contest/{contestId}>.
8. Repeat steps 1-7 every 5 minutes.

## Example contest details page markup

<html><head><style>body {transition: opacity ease-in 0.2s; }
body[unresolved] {opacity: 0; display: block; overflow: hidden; position: relative; }
</style><style type="text/css">
    .dk-spinner.loading-rules {
        position: absolute;
        top: 234px;
        left: 380px;
        border: 4px solid rgba(255, 255, 255, 0.2);
        border-left: 4px solid #fff;
    }
    .rm-prize-plus{
        padding-left: 3px;
    }
    .rm-prize-icon{
        line-height: 17px;
        cursor: pointer;
        position: relative;
    }
    .rm-prize-quantity{
        display:none;
        position: absolute;
        background-color: #000000;
        top: -20px;
        left: 0px;
        padding: 2px 4px;
        opacity: 1;
        white-space: nowrap;
    }
</style>
<script>
    window.mvcVars = window.mvcVars || {};
    window.mvcVars.showReignmakersMerchInDFS = false;
    function showTooltip(element) {
        var tooltip = element.querySelector('.tooltip.rm-prize-quantity');
        tooltip.style.display = 'block';
    }

    function hideTooltip(element) {
        var tooltip = element.querySelector('.tooltip.rm-prize-quantity');
        tooltip.style.display = 'none';
    }
</script>
<style>
    cubby-highlight {
            visibility: visible!important;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
    }

    cubby-highlight[data-type="user"] {
            transition: background-color .12s;
            background-color: rgba(245, 177, 64, 0.3);
            text-decoration-color: rgba(245, 177, 64, 0.9)!important;
    }
    
    cubby-highlight[data-type="user"]:hover {
            cursor: pointer;
    }
    
    cubby-highlight[data-type="user"][data-has-notes="true"] {
            text-decoration: underline;
            text-decoration-thickness: 3px;
    }
    
    cubby-highlight[data-type="user"][data-is-current-user="true"][data-active="true"] {
            background-color: rgba(245, 177, 64, 0.6);
    }
    
    cubby-highlight[data-type="user"][data-is-current-user="false"] {
            background-color: rgba(132, 90, 185, 0.3);
            text-decoration-color: rgba(132, 90, 185, 0.9)!important;
    }
    
    cubby-highlight[data-type="user"][data-is-current-user="false"][data-active="true"] {
            background-color: rgba(132, 90, 185, 0.6);
    }

    cubby-highlight[data-type="flash"] {
            transition: background-color 0.6s;
    }

    cubby-highlight[data-type="flash"][data-flash-active="true"] {
            background-color: rgba(115, 64, 221, 0.6)!important;
    }
</style><style class="automa-element-selector">@font-face { font-family: "Inter var"; font-weight: 100 900; font-display: swap; font-style: normal; font-named-instance: "Regular"; src: url("chrome-extension://infppggnoaenmfagbfknfkancpbljcca/Inter-roman-latin.var.woff2") format("woff2") }
.automa-element-selector { direction: ltr }
 [automa-isDragging] { user-select: none }
 [automa-el-list] {outline: 2px dashed #6366f1;}</style></head><body><div id="contest-details-pop" class="dk-drk-thm multi-entry no-lineups" data-contest-name="NFL $2.5M Thursday Kickoff Millionaire [$1M to 1st] (BAL @ KC)" data-contest-img="https://dk-email-marketing-content.s3.amazonaws.com/NFL/2020-2021/Contest+Logos/Logo_250x200_FFM.png" data-contest-id="164284870" data-draft-start-time="9/6/2024 12:20:00 AM" data-contest-sport="NFL" tabindex="0" role="dialog" aria-labelledby="dialog1Title">
    <div class="header">
        <div class="pull-left contest-info">
                <div class="contest-logo">
                    <img src="https://dk-email-marketing-content.s3.amazonaws.com/NFL/2020-2021/Contest+Logos/Logo_250x200_FFM.png" alt="Contest Logo">
                </div>
            <h2 data-test-id="contest-name" id="dialog1Title" title="NFL $2.5M Thursday Kickoff Millionaire [$1M to 1st] (BAL @ KC)">NFL $2.5M Thursday Kickoff Millionaire [$1M to 1st] (BAL @ KC)</h2>
            <div class="well dk-well dk-well-inline dk-well-xs">
                <label class="dk-gold">Entries:</label>
                <p><span class="contest-entries">53694</span>/<span data-test-id="contest-seats">196K</span></p>
            </div>
            <div class="well dk-well dk-well-inline dk-well-xs">
                <label class="dk-gold">Entry:</label>
                <p data-test-id="contest-entry-fee">$15</p>
            </div>
            <div class="well dk-well dk-well-inline dk-well-xs">
                <label class="dk-gold">Prizes:</label>
                    <p data-test-id="contest-total-prizes">$2,500,000</p>
            </div>
            <div class="well dk-well dk-well-inline dk-well-xs">
                <label class="dk-gold">Crowns:</label>
                <p data-test-id="contest-fpps">15</p>
            </div>
        </div>
            <div class="pull-left user-info">
                <p>
                    <span>Balance:</span> <span class="account-balance">
$3,935.04                    </span>
                </p>
                <p><span>My Entries:</span> <span class="dk-gold current-entries">0</span></p>
                <p style="display:none">
                    <span style="width: auto;">Free w/ Tickets:</span> <span class="dk-gold available-tickets">0</span>
                </p>
                <p>
                        <span>Multi-Entry:</span><span data-test-id="contest-multi-entry">150</span>

                </p>
            </div>
                    <div class="pull-right">
                <div class="well dk-well dk-well-xs countdown">
                    <label>Live In:</label>
                    <p class="cntr dk-gold" data-start="1725582000000">--:--:--</p>
                    <div class="full-date">
                        <p class="text-muted">
                            <small>09/05 8:20 PM EST</small>
                        </p>
                    </div>
                </div>
            </div>
    </div>
    <div class="clearfix"></div>
    <ul class="nav nav-tabs dk-tabs-orange" role="tablist">
        <li role="none" class="active">
            <a data-toggle="tab" href="#details-wrap" id="modal-details-tab" role="tab" aria-controls="details-wrap" tabindex="0" aria-selected="true">Contest Details</a>
        </li>
            <li role="none"><a data-toggle="tab" id="modal-rules-tab" aria-controls="rules-and-scoring-wrap" href="#rules-and-scoring-wrap" role="tab" tabindex="-1" aria-selected="false">Rules &amp; Scoring</a></li>
    </ul>
    <div class="tab-content">
        <div id="details-wrap" aria-labelledby="modal-details-tab" tabindex="0" class="tab-pane active">

<style type="text/css">
    .resizable-summary {
        font-weight: 600;
    }
    .resizable-summary a {
        color: #00b1c4;
        font-weight: 600;
    }
    .rm-prize-plus{
        padding: 0 2px;
    }
</style>
<div class="rounded-panel">
    <div class="left">
        <div class="dk-black-rounded-panel summary">
            <label>Summary</label>
                <div class="panel-body">
                    This 196078-player contest features $2,500,000.00 in total prizes and pays out the top 39880 finishing positions. First place wins $1,000,000.00.
                    <br><br>

                </div>
        </div>
        <div class="dk-black-rounded-panel entrants-list">
            <label>Entrants</label>
            <div class="input-group search-bar">
                <input type="text" class="form-control input-sm" id="search-input" aria-label="Search Entrants" placeholder="Search for an entrant...">
                <span class="input-group-addon"><i class="icon-search"></i></span>
            </div>
            <div class="panel-body">
                    <div id="entrants-layer">
                        <table id="entrants-table" class="dk-grid entrants-table">
                            <tbody>

        <tr>
        <td data-un="aanderson61"><span title="aanderson61" class="entrant-username">aanderson61</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="7 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="jbro990"><span title="JBro990" class="entrant-username">JBro990</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="13 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="amay537"><span title="amay537" class="entrant-username">amay537</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="2 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        </tr><tr>
        <td data-un="redmenace57"><span title="RedMenace57" class="entrant-username">RedMenace57</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="25 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="proscout4"><span title="proscout4" class="entrant-username">proscout4</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="2 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="jxs007"><span title="Jxs007" class="entrant-username">Jxs007</span> <span title="Experience Badge" class="icon-experienced-user-3"></span> <span class="bdg multi-entry-bdg-legacy" title="6 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        </tr><tr>
        <td data-un="smittyboys"><span title="SmittyBoys" class="entrant-username">SmittyBoys</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="4 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="cahgeo76"><span title="cahgeo76" class="entrant-username">cahgeo76</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="2 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="adamscrogham"><span title="adamscrogham" class="entrant-username">adamscrogham</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="13 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        </tr><tr>
        <td data-un="anthony79416"><span title="anthony79416" class="entrant-username">anthony79416</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="2 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="dannydimes75"><span title="dannydimes75" class="entrant-username">dannydimes75</span></td>
        <td data-un="ski68"><span title="Ski68" class="entrant-username">Ski68</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="5 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        </tr><tr>
        <td data-un="jerrysports369"><span title="Jerrysports369" class="entrant-username">Jerrysports369</span> <span title="Experience Badge" class="icon-experienced-user-4"></span> <span class="bdg multi-entry-bdg-legacy" title="3 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="zaneenglind5"><span title="zaneenglind5" class="entrant-username">zaneenglind5</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        <td data-un="slim45txag"><span title="Slim45txag" class="entrant-username">Slim45txag</span> <span title="Experience Badge" class="icon-experienced-user-2"></span></td>
        </tr><tr>
        <td data-un="jwack17"><span title="jwack17" class="entrant-username">jwack17</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="13 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="vegas107"><span title="Vegas107" class="entrant-username">Vegas107</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="3 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="kerson1998"><span title="kerson1998" class="entrant-username">kerson1998</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        </tr><tr>
        <td data-un="bigtimepillot"><span title="Bigtimepillot" class="entrant-username">Bigtimepillot</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        <td data-un="qqqqtastic78"><span title="QQQQtastic78" class="entrant-username">QQQQtastic78</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        <td data-un="drbrad"><span title="DrBrad" class="entrant-username">DrBrad</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        </tr><tr>
        <td data-un="td33dzul"><span title="td33dzul" class="entrant-username">td33dzul</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="10 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="mkiderman"><span title="mkiderman" class="entrant-username">mkiderman</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        <td data-un="mks99"><span title="mks99" class="entrant-username">mks99</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        </tr><tr>
        <td data-un="bamamike2267"><span title="bamamike2267" class="entrant-username">bamamike2267</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        <td data-un="claymore2017"><span title="Claymore2017" class="entrant-username">Claymore2017</span> <span title="Experience Badge" class="icon-experienced-user-3"></span> <span class="bdg multi-entry-bdg-legacy" title="43 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="iparks15"><span title="iparks15" class="entrant-username">iparks15</span> <span title="Experience Badge" class="icon-experienced-user-4"></span></td>
        </tr><tr>
        <td data-un="dbrown2"><span title="dbrown2" class="entrant-username">dbrown2</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        <td data-un="warmcleaver2"><span title="warmcleaver2" class="entrant-username">warmcleaver2</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="8 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="lumpyled"><span title="lumpyled" class="entrant-username">lumpyled</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        </tr><tr>
        <td data-un="sabresfan7"><span title="Sabresfan7" class="entrant-username">Sabresfan7</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        <td data-un="daddy277"><span title="daddy277" class="entrant-username">daddy277</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        <td data-un="fightinminidachshund"><span title="FightinMiniDachshund" class="entrant-username">FightinMiniDachshund</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="3 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        </tr><tr>
        <td data-un="mcv087"><span title="mcv087" class="entrant-username">mcv087</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="19 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="nathanridgewayy"><span title="nathanridgewayy" class="entrant-username">nathanridgewayy</span></td>
        <td data-un="gutp"><span title="gutp" class="entrant-username">gutp</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="150 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        </tr><tr>
        <td data-un="skunkape16"><span title="SkunkApe16" class="entrant-username">SkunkApe16</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="65 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="skraus90"><span title="skraus90" class="entrant-username">skraus90</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="24 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="fantasycannibal"><span title="FantasyCannibal" class="entrant-username">FantasyCannibal</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        </tr><tr>
        <td data-un="lights2002"><span title="lights2002" class="entrant-username">lights2002</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        <td data-un="goonerusa"><span title="goonerusa" class="entrant-username">goonerusa</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="150 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="rostrow19"><span title="rostrow19" class="entrant-username">rostrow19</span> <span title="Experience Badge" class="icon-experienced-user-4"></span></td>
        </tr><tr>
        <td data-un="endwell1"><span title="Endwell1" class="entrant-username">Endwell1</span> <span title="Experience Badge" class="icon-experienced-user-2"></span> <span class="bdg multi-entry-bdg-legacy" title="2 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="shomesue"><span title="SHOMESUE" class="entrant-username">SHOMESUE</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        <td data-un="thud559"><span title="thud559" class="entrant-username">thud559</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="19 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        </tr><tr>
        <td data-un="jtmartin3"><span title="jtmartin3" class="entrant-username">jtmartin3</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="42 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="wearethelimits"><span title="wearethelimits" class="entrant-username">wearethelimits</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="3 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="muddad"><span title="Muddad" class="entrant-username">Muddad</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="3 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        </tr><tr>
        <td data-un="patsnation47"><span title="Patsnation47" class="entrant-username">Patsnation47</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="4 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="drj23911"><span title="DrJ23911" class="entrant-username">DrJ23911</span> <span title="Experience Badge" class="icon-experienced-user-3"></span></td>
        <td data-un="wrrnjns"><span title="wrrnjns" class="entrant-username">wrrnjns</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="2 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        </tr><tr>
        <td data-un="biggbabe100"><span title="Biggbabe100" class="entrant-username">Biggbabe100</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        <td data-un="bmanbiz11"><span title="Bmanbiz11" class="entrant-username">Bmanbiz11</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        <td data-un="kobe4prez24"><span title="kobe4prez24" class="entrant-username">kobe4prez24</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="2 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        </tr><tr>
        <td data-un="isaiahsignup"><span title="isaiahsignup" class="entrant-username">isaiahsignup</span> <span title="Experience Badge" class="icon-experienced-user-4"></span> <span class="bdg multi-entry-bdg-legacy" title="2 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="bingolow17"><span title="Bingolow17" class="entrant-username">Bingolow17</span></td>
        <td data-un="bkraft1122"><span title="Bkraft1122" class="entrant-username">Bkraft1122</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="5 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        </tr><tr>
        <td data-un="wonderboy1968"><span title="wonderboy1968" class="entrant-username">wonderboy1968</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="58 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="rasiefert"><span title="rasiefert" class="entrant-username">rasiefert</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="3 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="stevebutrang"><span title="stevebutrang" class="entrant-username">stevebutrang</span></td>
        </tr><tr>
        <td data-un="nicky_knuckles"><span title="Nicky_Knuckles" class="entrant-username">Nicky_Knuckles</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="7 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="raiderdane"><span title="RaiderDane" class="entrant-username">RaiderDane</span> <span title="Experience Badge" class="icon-experienced-user-3"></span> <span class="bdg multi-entry-bdg-legacy" title="5 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="mirishb79"><span title="mirishb79" class="entrant-username">mirishb79</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="4 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        </tr><tr>
        <td data-un="chris9er87"><span title="Chris9er87" class="entrant-username">Chris9er87</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        <td data-un="walk_of_shane"><span title="walk_of_shane" class="entrant-username">walk_of_shane</span></td>
        <td data-un="aiglesia1"><span title="aiglesia1" class="entrant-username">aiglesia1</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        </tr><tr>
        <td data-un="zeechamp"><span title="Zeechamp" class="entrant-username">Zeechamp</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="150 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="firefox952"><span title="firefox952" class="entrant-username">firefox952</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="10 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="yonvys"><span title="YONVYS" class="entrant-username">YONVYS</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="6 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        </tr><tr>
        <td data-un="chillzone34"><span title="chillzone34" class="entrant-username">chillzone34</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="3 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="matador23"><span title="matador23" class="entrant-username">matador23</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        <td data-un="bigfootrod"><span title="bigfootrod" class="entrant-username">bigfootrod</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        </tr><tr>
        <td data-un="jasonjmax"><span title="jasonjmax" class="entrant-username">jasonjmax</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="2 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="jjparrish"><span title="jjparrish" class="entrant-username">jjparrish</span></td>
        <td data-un="scooter8210"><span title="scooter8210" class="entrant-username">scooter8210</span> <span title="Experience Badge" class="icon-experienced-user-4"></span></td>
        </tr><tr>
        <td data-un="rubymmk"><span title="rubymmk" class="entrant-username">rubymmk</span> <span title="Experience Badge" class="icon-experienced-user-4"></span> <span class="bdg multi-entry-bdg-legacy" title="2 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="lebowski072"><span title="Lebowski072" class="entrant-username">Lebowski072</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="2 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="88hardball88"><span title="88hardball88" class="entrant-username">88hardball88</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        </tr><tr>
        <td data-un="reynelda77"><span title="reynelda77" class="entrant-username">reynelda77</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="73 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="brenden09"><span title="brenden09" class="entrant-username">brenden09</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        <td data-un="coupeman17"><span title="Coupeman17" class="entrant-username">Coupeman17</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="5 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        </tr><tr>
        <td data-un="mytyers"><span title="mytyers" class="entrant-username">mytyers</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="7 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="upsetalert"><span title="UpsetAlert" class="entrant-username">UpsetAlert</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="4 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="benglasfan4life115"><span title="BenglasFan4Life115" class="entrant-username">BenglasFan4Life115</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="16 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        </tr><tr>
        <td data-un="unluck1313"><span title="unluck1313" class="entrant-username">unluck1313</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        <td data-un="supercatsr"><span title="supercatsr" class="entrant-username">supercatsr</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        <td data-un="miclo81"><span title="miclo81" class="entrant-username">miclo81</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        </tr><tr>
        <td data-un="nomiabd"><span title="nomiabd" class="entrant-username">nomiabd</span> <span title="Experience Badge" class="icon-experienced-user-5"></span></td>
        <td data-un="kmsurfs2000"><span title="kmsurfs2000" class="entrant-username">kmsurfs2000</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="2 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="subsammy"><span title="SubSammy" class="entrant-username">SubSammy</span> <span title="Experience Badge" class="icon-experienced-user-4"></span></td>
        </tr><tr>
        <td data-un="tonk265"><span title="Tonk265" class="entrant-username">Tonk265</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="13 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="hypegotti"><span title="hypegotti" class="entrant-username">hypegotti</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="6 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="gmgriff33"><span title="gmgriff33" class="entrant-username">gmgriff33</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="8 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        </tr><tr>
        <td data-un="jcvinci"><span title="jcvinci" class="entrant-username">jcvinci</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="18 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="mikeyjpjr2345"><span title="mikeyjpjr2345" class="entrant-username">mikeyjpjr2345</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="5 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="ddelpha"><span title="ddelpha" class="entrant-username">ddelpha</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="2 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        </tr><tr>
        <td data-un="kingburg"><span title="kingburg" class="entrant-username">kingburg</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="3 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="tommylamasa"><span title="Tommylamasa" class="entrant-username">Tommylamasa</span> <span title="Experience Badge" class="icon-experienced-user-4"></span> <span class="bdg multi-entry-bdg-legacy" title="3 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>
        <td data-un="thesportsbanter"><span title="thesportsbanter" class="entrant-username">thesportsbanter</span> <span title="Experience Badge" class="icon-experienced-user-5"></span> <span class="bdg multi-entry-bdg-legacy" title="2 entries"><span class="icon-multi-entry my-contest-icon-multi-entry" role="img" aria-label="multi entry icon"></span></span></td>

    </tr>

                            </tbody>
                        </table>
                    </div>
                    <table id="entrants-search" class="dk-grid" style="display: none;">
                        <tbody></tbody>
                    </table>
            </div>
        </div>
    </div>
    <div class="dk-black-rounded-panel prize-payouts">
        <label>Prize Payouts</label>
        <div class="panel-body">
                    <table class="dk-grid" tabindex="0">
                        <tbody><tr class="accessible-hidden-header">
                            <th>Position Count</th>
                            <th>Description</th>
                        </tr>
                            <tr>
                                <td>1st</td>
                                <td>$1,000,000.00</td>
                            </tr>
                            <tr>
                                <td>2nd</td>
                                <td>$100,000.00</td>
                            </tr>
                            <tr>
                                <td>3rd</td>
                                <td>$50,000.00</td>
                            </tr>
                            <tr>
                                <td>4th</td>
                                <td>$25,000.00</td>
                            </tr>
                            <tr>
                                <td>5th</td>
                                <td>$20,000.00</td>
                            </tr>
                            <tr>
                                <td>6th</td>
                                <td>$15,000.00</td>
                            </tr>
                            <tr>
                                <td>7th - 8th</td>
                                <td>$12,500.00</td>
                            </tr>
                            <tr>
                                <td>9th - 10th</td>
                                <td>$10,000.00</td>
                            </tr>
                            <tr>
                                <td>11th - 12th</td>
                                <td>$7,500.00</td>
                            </tr>
                            <tr>
                                <td>13th - 15th</td>
                                <td>$5,000.00</td>
                            </tr>
                            <tr>
                                <td>16th - 20th</td>
                                <td>$3,000.00</td>
                            </tr>
                            <tr>
                                <td>21st - 25th</td>
                                <td>$2,000.00</td>
                            </tr>
                            <tr>
                                <td>26th - 30th</td>
                                <td>$1,500.00</td>
                            </tr>
                            <tr>
                                <td>31st - 40th</td>
                                <td>$1,000.00</td>
                            </tr>
                            <tr>
                                <td>41st - 50th</td>
                                <td>$750.00</td>
                            </tr>
                            <tr>
                                <td>51st - 65th</td>
                                <td>$500.00</td>
                            </tr>
                            <tr>
                                <td>66th - 90th</td>
                                <td>$300.00</td>
                            </tr>
                            <tr>
                                <td>91st - 125th</td>
                                <td>$200.00</td>
                            </tr>
                            <tr>
                                <td>126th - 175th</td>
                                <td>$150.00</td>
                            </tr>
                            <tr>
                                <td>176th - 250th</td>
                                <td>$100.00</td>
                            </tr>
                            <tr>
                                <td>251st - 400th</td>
                                <td>$80.00</td>
                            </tr>
                            <tr>
                                <td>401st - 800th</td>
                                <td>$60.00</td>
                            </tr>
                            <tr>
                                <td>801st - 2000th</td>
                                <td>$50.00</td>
                            </tr>
                            <tr>
                                <td>2001st - 5000th</td>
                                <td>$40.00</td>
                            </tr>
                            <tr>
                                <td>5001st - 13000th</td>
                                <td>$30.00</td>
                            </tr>
                            <tr>
                                <td>13001st - 39880th</td>
                                <td>$25.00</td>
                            </tr>
                    </tbody></table>
        </div>
    </div>
</div>
<div class="clearfix"></div>
<div class="footer">
    <div class="footer-links">
        <div class="HEP-info">
            <span class="icon-experienced-user"></span>
            <span><a href="/experience-badges" target="_blank">Experience Badge</a></span>
        </div>
        <div class="AvgRes-info">
            <span class="icon-average-results"></span>
            <span><a href="/average-results" target="_blank">Average Results</a></span>
        </div>
        <div class="ResGam-info">
            <span class="icon-shield"></span>
            <span><a href="/responsible-gaming" target="_blank">Responsible Gaming</a></span>
        </div>
    </div>
    <div class="footer-buttons">
            <a href="/contest/draftteam/164284870" class="btn dk-btn-gold" id="contest-details-enter">Draft Team</a>
        <a href="#" class="btn dk-btn-lgt-grey" onclick="$.fancybox.close();return false;">Close</a>
    </div>
</div>
<script type="text/javascript">
    $('a#contest-details-enter').on('click', function (e) {
        e.preventDefault();
        var link = $(this).attr('href');

        if (window.DK && window.DK.Lobby && window.DK.Lobby.trackLobbyEvent) {
            var contestId = null;
            var contestDetailsOptions = {};
            if (window.DK.ContestDetailsPop) {
                contestDetailsOptions = window.DK.ContestDetailsPop.getOptions();
                contestId = contestDetailsOptions.contestId;
            }
            
            if (window.DK.Lobby.trackGameStyleEvent) {
                var draftGroupId = contestDetailsOptions.draftGroupId;
                var contestId = contestDetailsOptions.contestId;
                var sport = contestDetailsOptions.sport;
                window.DK.Lobby.trackGameStyleEvent('click_modal_draft_team', draftGroupId, contestId, sport);
            }

            window.DK.Lobby.trackLobbyEvent("Contests Filtered", {
                "Contest Entry": "Contest Details",
                "contestId": contestId
            },
            function () {
                window.location.href = link;
            });
        } else {
            window.location.href = link;
        }
    });
</script>
        </div>
            <div id="rules-and-scoring-wrap" aria-labelledby="modal-rules-tab" tabindex="0" class="tab-pane">
                <div id="dkjs-rules-and-scoring-container" class="legacy" style="padding-bottom: 10px">
                    <div class="dk-spinner loading-rules"></div>
                </div>
                <div class="footer">
                    <div class="footer-links">
                        <div class="HEP-info">
                            <span class="icon-experienced-user"></span>
                            <span><a href="/experience-badges" target="_blank">Experience Badge</a></span>
                        </div>
                        <div class="AvgRes-info">
                            <span class="icon-average-results"></span>
                            <span><a href="/average-results" target="_blank">Average Results</a></span>
                        </div>
                        <div class="ResGam-info">
                            <span class="icon-shield"></span>
                            <span><a href="/responsible-gaming" target="_blank">Responsible Gaming</a></span>
                        </div>
                    </div>
                    <div class="footer-buttons">
                            <a href="/contest/draftteam/164284870" class="btn dk-btn-gold">Draft Team</a>
                        <a href="#" class="btn dk-btn-lgt-grey" tabindex="0" onclick="$.fancybox.close();return false;">Close</a>
                    </div>
                </div>
            </div>
    </div>
</div>
<script type="text/javascript">

    $(window).off('dkContestDetailsPop.renderComplete').on('dkContestDetailsPop.renderComplete', function () {
        var pop = DK.ContestDetailsPop.init({
            currentEntries: 53694,
            maxEntries: 196078,
            userEntries: 0,
            maxUserEntries: 150,
            userBalance: 3935.040000000,
            redeemableTickets: 0,
            contestId: 164284870,
            contestStatusId: 1,
            contestTicketOnlyEntry: false,
            contestCost: 15.0000,
            maxEntriesPerRequest: 300
            });
        DK.ContestDetailsPop.Paging.init(pop, 99);
        DK.ContestDetailsPop.Search.init(pop, 99);
        window.pixel.fireContestPop(164284870, 'NFL', 15.0000);
        $('#contest-details-pop').focus();
        $(window).trigger('dkjs-dkContestDetailsPop.renderComplete', {contestId: 164284870, draftGroupId: 0});
    });
</script>
</div>
</body>
</html>

## Preferred Tech Stack

- Conda for virtual environments
- AgentQL for website scraping (<https://docs.agentql.com/quick-start>)
- Python 3.11+
- Slack API for sending messages
- Supabase for database
- schedule (python library) for scheduling tasks

## Timeline

- 3 weeks
- I want to start coding in 3 days

## Notes

- We may need to do some research on how to do this. Let me know if you don't know how to perform a task and I will research it.
